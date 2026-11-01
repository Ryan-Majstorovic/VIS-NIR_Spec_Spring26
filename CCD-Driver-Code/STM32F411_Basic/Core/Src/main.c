/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usb_device.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "usbd_cdc_if.h"
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include "ccd_timing.h"

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */
/* DOC-UUID: 9F6C2C68-53B8-4B6B-BB9F-42068A583BF3 */
#define CCD_LINE_SAMPLE_COUNT 3694U
#define CCD_EFFECTIVE_START_INDEX 32U
#define CCD_EFFECTIVE_SAMPLE_COUNT 3648U
#define CCD_FRAME_BUFFER_COUNT 4U
#define CCD_FRAME_TX_TIMEOUT_MS 20U
#define CCD_USB_HEADER_BYTES 28U
#define CCD_USB_PAYLOAD_BYTES (CCD_LINE_SAMPLE_COUNT * sizeof(uint16_t))
#define CCD_USB_FRAME_BYTES (CCD_USB_HEADER_BYTES + CCD_USB_PAYLOAD_BYTES)

typedef struct __attribute__((packed))
{
  uint32_t magic;
  uint8_t version;
  uint8_t packet_type;
  uint16_t reserved;
  uint32_t frame_id;
  uint16_t sample_count;
  uint16_t effective_start;
  uint16_t effective_count;
  uint16_t flags;
  uint32_t payload_bytes;
  uint32_t integration_us;
} CcdUsbFrameHeader;

typedef struct
{
  CcdUsbFrameHeader header;
  uint16_t samples[CCD_LINE_SAMPLE_COUNT];
} CcdUsbFramePacket;

typedef struct
{
  CcdUsbFramePacket packet;
  volatile uint16_t flags;
  volatile uint8_t ready;
} CcdFrameSlot;

typedef char CcdUsbFrameHeaderSizeCheck[(sizeof(CcdUsbFrameHeader) == CCD_USB_HEADER_BYTES) ? 1 : -1];
typedef char CcdUsbFramePacketSizeCheck[(sizeof(CcdUsbFramePacket) == CCD_USB_FRAME_BYTES) ? 1 : -1];

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
enum
{
  CCD_PACKET_MAGIC = 0x31444343UL,
  CCD_PACKET_VERSION = 2U,
  CCD_PACKET_TYPE_FRAME = 1U
};

enum
{
  CCD_FRAME_FLAG_ICG_SYNC = (1U << 0),
  CCD_FRAME_FLAG_TIMING_FAULT = (1U << 1),
  CCD_FRAME_FLAG_USB_TIMEOUT = (1U << 2)
};

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;
DMA_HandleTypeDef hdma_adc1;
DMA_HandleTypeDef hdma_tim3_up;
DMA_HandleTypeDef hdma_tim4_up;

TIM_HandleTypeDef htim1;
TIM_HandleTypeDef htim2;
TIM_HandleTypeDef htim3;
TIM_HandleTypeDef htim4;
TIM_HandleTypeDef htim5;

/* USER CODE BEGIN PV */
CcdFrameSlot ccd_frame_slots[CCD_FRAME_BUFFER_COUNT];
volatile int8_t ccd_active_slot = -1;
volatile int8_t ccd_sending_slot = -1;
volatile uint8_t ccd_next_tx_slot = 0;
volatile uint32_t ccd_icg_cycle_counter = 0;
volatile uint32_t ccd_frame_counter = 0;
volatile uint32_t ccd_dma_half_count = 0;
volatile uint32_t ccd_dma_full_count = 0;
volatile uint32_t ccd_icg_start_count = 0;
volatile uint32_t ccd_icg_end_count = 0;
volatile uint32_t ccd_dropped_frame_count = 0;
volatile uint32_t ccd_usb_timeout_count = 0;

static uint32_t ccd_integration_us = CCD_MIN_INTEGRATION_US;
static volatile uint32_t ccd_requested_us;
static volatile uint32_t ccd_applied_frame_id;
static volatile uint8_t ccd_reconfigure_ready;
static volatile uint8_t ccd_arm_due;
static volatile uint8_t ccd_discard_exposure;
static volatile uint8_t ccd_timing_fault;
static volatile uint8_t ccd_running;
static uint8_t ccd_fault_reported;
static uint32_t ccd_segment_count = 1U;
static uint32_t ccd_segment_index;
static CcdTimingSegment ccd_sh_schedule[CCD_MAX_SEGMENTS];
static CcdTimingSegment ccd_icg_schedule[CCD_MAX_SEGMENTS];
#define CCD_RX_BYTES 128U
static uint8_t ccd_rx[CCD_RX_BYTES];
static volatile uint16_t ccd_rx_head, ccd_rx_tail;
static volatile uint8_t ccd_rx_overflow;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_ADC1_Init(void);
static void MX_DMA_Init(void);
static void MX_TIM1_Init(void);
static void MX_TIM2_Init(void);
static void MX_TIM3_Init(void);
static void MX_TIM4_Init(void);
static void MX_TIM5_Init(void);
/* USER CODE BEGIN PFP */
static void SendStatusLine(const char *text);
static uint8_t CDC_Transmit_Blocking(const uint8_t *buffer, uint16_t length, uint32_t timeout_ms);
static uint8_t CDC_WaitForTxReady(uint32_t timeout_ms);
static void PrepareFrameHeader(uint32_t slot_index, uint32_t frame_id, uint16_t flags);
static void ArmFrameCapture(void);
static void StartTiming(uint32_t integration_us);
static void StopTiming(void);
static void PollTimingCommands(void);
static void HandleFrameBoundary(void);
static void AbortActiveCapture(uint16_t fault_flags);
static int32_t AcquireFrameSlot(void);
static int32_t FindNextReadyFrameSlot(void);
static uint8_t SendFrameSlot(uint32_t slot_index);
static void ReleaseFrameSlot(uint32_t slot_index);

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
/* All timer-register changes below occur with the waveform engine stopped. */
static void StopTiming(void)
{
  uint32_t primask = __get_PRIMASK();
  __disable_irq();
  /* Finish an emitted SH pulse before stopping a normal reconfiguration.
     Fault shutdown takes priority over waveform completion. */
  if (ccd_running != 0U && ccd_timing_fault == 0U && (TIM3->CR1 & TIM_CR1_CEN)) {
    while (TIM3->CCR1 != 0U &&
           (TIM3->CNT < TIM3->CCR1 || TIM3->CNT + 2U >= TIM3->ARR)) { }
  }
  ccd_running = 0U;
  TIM3->CR1 &= ~TIM_CR1_CEN;
  TIM4->CR1 &= ~TIM_CR1_CEN;
  TIM1->CR1 &= ~TIM_CR1_CEN;
  TIM1->BDTR &= ~TIM_BDTR_MOE;
  TIM3->DIER = 0U;
  TIM4->DIER = 0U;
  TIM3->CR1 &= ~TIM_CR1_CEN;
  TIM4->CR1 &= ~TIM_CR1_CEN;
  TIM3->CCER &= ~TIM_CCER_CC1E;
  TIM4->CCER &= ~TIM_CCER_CC1E;
  TIM2->CR1 &= ~TIM_CR1_CEN;
  __set_PRIMASK(primask);
  (void)HAL_ADC_Stop_DMA(&hadc1);
  if (hdma_tim3_up.Instance != NULL) (void)HAL_DMA_Abort(&hdma_tim3_up);
  if (hdma_tim4_up.Instance != NULL) (void)HAL_DMA_Abort(&hdma_tim4_up);
  ccd_active_slot = -1;
}

static void TimingDmaError(DMA_HandleTypeDef *dma)
{
  (void)dma;
  ccd_timing_fault = 1U;
}

static void StartScheduleDma(TIM_HandleTypeDef *timer, DMA_HandleTypeDef *dma,
                             DMA_Stream_TypeDef *stream, uint32_t channel,
                             CcdTimingSegment *schedule)
{
  dma->Instance = stream;
  dma->Init.Channel = channel;
  dma->Init.Direction = DMA_MEMORY_TO_PERIPH;
  dma->Init.PeriphInc = DMA_PINC_DISABLE;
  dma->Init.MemInc = DMA_MINC_ENABLE;
  dma->Init.PeriphDataAlignment = DMA_PDATAALIGN_WORD;
  dma->Init.MemDataAlignment = DMA_MDATAALIGN_WORD;
  dma->Init.Mode = DMA_CIRCULAR;
  dma->Init.Priority = DMA_PRIORITY_HIGH;
  dma->Init.FIFOMode = DMA_FIFOMODE_DISABLE;
  if (HAL_DMA_Init(dma) != HAL_OK) { ccd_timing_fault = 1U; return; }
  dma->XferErrorCallback = TimingDmaError;
  /* ARR, reserved RCR (zero), CCR1 are one contiguous hardware DMA burst. */
  timer->Instance->DCR = TIM_DMABASE_ARR | TIM_DMABURSTLENGTH_3TRANSFERS;
  if (HAL_DMA_Start_IT(dma, (uint32_t)schedule,
                       (uint32_t)&timer->Instance->DMAR, ccd_segment_count * 3U) != HAL_OK) {
    ccd_timing_fault = 1U;
    return;
  }
  /* Wrap completion is not a physical frame interrupt; retain error interrupts only. */
  __HAL_DMA_DISABLE_IT(dma, DMA_IT_HT | DMA_IT_TC);
  timer->Instance->DIER |= TIM_DIER_UDE;
}

static void StartTiming(uint32_t integration_us)
{
  TIM_SlaveConfigTypeDef slave = {0};
  StopTiming();
  for (uint32_t i = 0U; i < CCD_FRAME_BUFFER_COUNT; ++i) ccd_frame_slots[i].ready = 0U;
  ccd_integration_us = integration_us;
  ccd_discard_exposure = 1U;
  ccd_reconfigure_ready = 0U;
  ccd_arm_due = 0U;
  ccd_segment_index = 0U;
  ccd_segment_count = integration_us <= CCD_BASE_FRAME_US ? 1U : CcdSegmentCount(integration_us);
  TIM3->SMCR = 0U;
  TIM4->SMCR = 0U;
  TIM3->CR1 = TIM_CR1_ARPE;
  TIM4->CR1 = TIM_CR1_ARPE;
  TIM3->PSC = CCD_TIMER_PRESCALER;
  TIM4->PSC = CCD_TIMER_PRESCALER;
  TIM3->CCMR1 = TIM_OCMODE_PWM1 | TIM_CCMR1_OC1PE;
  TIM4->CCMR1 = TIM_OCMODE_PWM2 | TIM_CCMR1_OC1PE;
  TIM3->CCER = 0U;
  TIM4->CCER = CCD_ICG_INVERT_OUTPUT ? TIM_CCER_CC1P : 0U;
  TIM4->CR2 = TIM_TRGO_OC1REF;

  CcdTimingSegment first_sh, first_icg;
  if (integration_us <= CCD_BASE_FRAME_US) {
    first_sh = (CcdTimingSegment){integration_us * 2U - 1U, 0U, CCD_SH_HIGH_TICKS};
    first_icg = (CcdTimingSegment){CCD_BASE_FRAME_US * 2U - 1U, 0U,
                                 (CCD_BASE_FRAME_US - CCD_READOUT_US) * 2U};
  } else {
    first_sh = CcdSegment(integration_us, 0U, 1U);
    first_icg = CcdSegment(integration_us, 0U, 0U);
  }
  /* TIM4 starts segment 0 immediately. Its first update latches segment 1. */
  TIM4->ARR = first_icg.arr;
  TIM4->CCR1 = first_icg.ccr;
  TIM4->EGR = TIM_EGR_UG;
  TIM4->CNT = 0U;
  if (ccd_segment_count > 1U) {
    CcdTimingSegment next = CcdSegment(integration_us, 1U, 0U);
    TIM4->ARR = next.arr;
    TIM4->CCR1 = next.ccr;
  }

  /* TIM3's initial wrap occurs one 0.5-us tick after common startup.
     That wrap latches segment 0 and emits SH; it must not skip its first segment. */
  CcdTimingSegment initial_sh = ccd_segment_count > 1U ?
      CcdSegment(integration_us, ccd_segment_count - 1U, 1U) : first_sh;
  TIM3->ARR = initial_sh.arr;
  TIM3->CCR1 = initial_sh.ccr;
  TIM3->EGR = TIM_EGR_UG;
  TIM3->CNT = initial_sh.arr;
  TIM3->ARR = first_sh.arr;
  TIM3->CCR1 = first_sh.ccr;

  if (ccd_segment_count > 1U) {
    for (uint32_t i = 0U; i < ccd_segment_count; ++i) {
      ccd_sh_schedule[i] = CcdSegment(integration_us, (i + 1U) % ccd_segment_count, 1U);
      ccd_icg_schedule[i] = CcdSegment(integration_us, (i + 2U) % ccd_segment_count, 0U);
    }
    StartScheduleDma(&htim3, &hdma_tim3_up, DMA1_Stream2, DMA_CHANNEL_5, ccd_sh_schedule);
    StartScheduleDma(&htim4, &hdma_tim4_up, DMA1_Stream6, DMA_CHANNEL_2, ccd_icg_schedule);
  }

  slave.SlaveMode = TIM_SLAVEMODE_TRIGGER;
  slave.InputTrigger = TIM_TS_ITR0; /* Both independent outputs start from TIM1. */
  if (HAL_TIM_SlaveConfigSynchro(&htim3, &slave) != HAL_OK ||
      HAL_TIM_SlaveConfigSynchro(&htim4, &slave) != HAL_OK) ccd_timing_fault = 1U;
  slave.InputTrigger = TIM_TS_ITR3; /* TIM4 OC1REF rising is CCD ICG rising after U1 inversion. */
  if (HAL_TIM_SlaveConfigSynchro(&htim2, &slave) != HAL_OK) ccd_timing_fault = 1U;
  TIM2->CCER |= TIM_CCER_CC1E;
  TIM3->SR = 0U;
  TIM4->SR = 0U;
  HAL_NVIC_ClearPendingIRQ(TIM4_IRQn);
  TIM4->DIER |= TIM_DIER_UIE | TIM_DIER_CC1IE;
  TIM3->CCER |= TIM_CCER_CC1E;
  TIM4->CCER |= TIM_CCER_CC1E;
  ArmFrameCapture();
  if (ccd_timing_fault != 0U) { StopTiming(); return; }

  /* Seed phiM inside its high half-cycle; board propagation must be scoped.
     Both APB timer clocks are 96 MHz in this clock tree. */
  TIM1->CR2 = TIM_TRGO_ENABLE;
  TIM1->EGR = TIM_EGR_UG;
  TIM1->CNT = CCD_MASTER_INITIAL_COUNTER;
  TIM1->SR = 0U;
  TIM1->CCER |= TIM_CCER_CC1E;
  TIM1->BDTR |= TIM_BDTR_MOE;
  ccd_running = 1U;
  TIM1->CR1 |= TIM_CR1_CEN; /* Single TRGO_ENABLE edge releases both slaves. */
}

void CCD_ReceiveCommandBytes(const uint8_t *bytes, uint32_t length)
{
  /* USB ISR is the sole producer; parsing and every USB write run in main. */
  for (uint32_t i = 0U; i < length; ++i) {
    uint16_t next = (uint16_t)((ccd_rx_head + 1U) % CCD_RX_BYTES);
    if (next == ccd_rx_tail) { ccd_rx_overflow = 1U; break; }
    ccd_rx[ccd_rx_head] = bytes[i];
    __DMB();
    ccd_rx_head = next;
  }
}

static void PollTimingCommands(void)
{
  static char line[48];
  static uint32_t used;
  static uint8_t discard;
  char response[96];
  if (ccd_rx_overflow != 0U) {
    __disable_irq();
    ccd_rx_tail = ccd_rx_head;
    ccd_rx_overflow = 0U;
    __enable_irq();
    used = 0U;
    discard = 1U;
    SendStatusLine("ERR INTEG OVERFLOW\r\n");
  }
  while (ccd_rx_tail != ccd_rx_head) {
    char c = (char)ccd_rx[ccd_rx_tail];
    ccd_rx_tail = (uint16_t)((ccd_rx_tail + 1U) % CCD_RX_BYTES);
    if (c == '\r') continue;
    if (c != '\n') {
      if (used + 1U < sizeof(line)) line[used++] = c;
      else discard = 1U;
      continue;
    }
    line[used] = '\0';
    if (discard != 0U) {
      SendStatusLine("ERR INTEG INVALID\r\n");
    } else if (strncmp(line, "INTEG ", 6U) == 0) {
      char *end;
      uint32_t us = (uint32_t)strtoul(line + 6U, &end, 10);
      uint8_t digits = used > 6U;
      for (uint32_t i = 6U; i < used; ++i)
        if (line[i] < '0' || line[i] > '9') digits = 0U;
      if (digits == 0U || *end != '\0' || !CcdIntegrationValid(us)) {
        SendStatusLine("ERR INTEG INVALID\r\n");
      } else if (ccd_timing_fault != 0U) {
        SendStatusLine("ERR INTEG TIMING\r\n");
      } else if (ccd_requested_us != 0U) {
        SendStatusLine("ERR INTEG BUSY\r\n");
      } else {
        ccd_requested_us = us;
        ccd_applied_frame_id = 0U;
        snprintf(response, sizeof(response), "PENDING INTEG %lu\r\n", (unsigned long)us);
        SendStatusLine(response);
      }
    } else {
      SendStatusLine("ERR COMMAND UNKNOWN\r\n");
    }
    used = 0U;
    discard = 0U;
  }
  if (ccd_reconfigure_ready != 0U) StartTiming(ccd_requested_us);
  if (ccd_timing_fault != 0U) {
    if (ccd_fault_reported == 0U) {
      ccd_fault_reported = 1U;
      StopTiming();
      /* Do not leak previously queued frames after a timing fault. */
      for (uint32_t i = 0U; i < CCD_FRAME_BUFFER_COUNT; ++i) ccd_frame_slots[i].ready = 0U;
      SendStatusLine("ERR INTEG TIMING\r\n");
      ccd_requested_us = 0U;
    }
  } else if (ccd_applied_frame_id != 0U) {
    snprintf(response, sizeof(response), "OK INTEG %lu %lu\r\n",
             (unsigned long)ccd_integration_us, (unsigned long)ccd_applied_frame_id);
    ccd_applied_frame_id = 0U;
    ccd_requested_us = 0U;
    SendStatusLine(response);
  }
}

static uint8_t CDC_Transmit_Blocking(const uint8_t *buffer, uint16_t length, uint32_t timeout_ms)
{
  uint32_t start_tick = HAL_GetTick();
  uint8_t status = USBD_BUSY;

  while ((HAL_GetTick() - start_tick) < timeout_ms)
  {
    status = CDC_Transmit_FS((uint8_t *)buffer, length);
    if (status == USBD_OK)
    {
      return USBD_OK;
    }
  }

  return status;
}

static void SendStatusLine(const char *text)
{
  (void)CDC_Transmit_Blocking((const uint8_t *)text, (uint16_t)strlen(text), 100U);
}

static uint8_t CDC_WaitForTxReady(uint32_t timeout_ms)
{
  uint32_t start_tick = HAL_GetTick();

  while ((HAL_GetTick() - start_tick) < timeout_ms)
  {
    if (CDC_TxReady_FS() != 0U)
    {
      return USBD_OK;
    }
  }

  return USBD_BUSY;
}

static void PrepareFrameHeader(uint32_t slot_index, uint32_t frame_id, uint16_t flags)
{
  CcdUsbFrameHeader *header = &ccd_frame_slots[slot_index].packet.header;

  header->magic = CCD_PACKET_MAGIC;
  header->version = CCD_PACKET_VERSION;
  header->packet_type = CCD_PACKET_TYPE_FRAME;
  header->reserved = 0U;
  header->frame_id = frame_id;
  header->sample_count = CCD_LINE_SAMPLE_COUNT;
  header->effective_start = CCD_EFFECTIVE_START_INDEX;
  header->effective_count = CCD_EFFECTIVE_SAMPLE_COUNT;
  header->flags = flags;
  header->payload_bytes = (uint32_t)CCD_USB_PAYLOAD_BYTES;
  header->integration_us = ccd_integration_us;
}

static int32_t AcquireFrameSlot(void)
{
  uint32_t slot_index;

  for (slot_index = 0U; slot_index < CCD_FRAME_BUFFER_COUNT; ++slot_index)
  {
    if ((int8_t)slot_index == ccd_active_slot)
    {
      continue;
    }

    if ((int8_t)slot_index == ccd_sending_slot)
    {
      continue;
    }

    if (ccd_frame_slots[slot_index].ready != 0U)
    {
      continue;
    }

    return (int32_t)slot_index;
  }

  return -1;
}

static int32_t FindNextReadyFrameSlot(void)
{
  uint32_t offset;

  for (offset = 0U; offset < CCD_FRAME_BUFFER_COUNT; ++offset)
  {
    uint32_t slot_index = (ccd_next_tx_slot + offset) % CCD_FRAME_BUFFER_COUNT;
    if (ccd_frame_slots[slot_index].ready != 0U)
    {
      ccd_next_tx_slot = (uint8_t)((slot_index + 1U) % CCD_FRAME_BUFFER_COUNT);
      return (int32_t)slot_index;
    }
  }

  return -1;
}

static void ReleaseFrameSlot(uint32_t slot_index)
{
  ccd_frame_slots[slot_index].ready = 0U;
  ccd_frame_slots[slot_index].flags = 0U;
  ccd_frame_slots[slot_index].packet.header.frame_id = 0U;
  ccd_frame_slots[slot_index].packet.header.flags = 0U;
}

static void AbortActiveCapture(uint16_t fault_flags)
{
  int8_t active_slot = ccd_active_slot;

  (void)HAL_ADC_Stop_DMA(&hadc1);
  __HAL_TIM_DISABLE(&htim2);

  if (active_slot >= 0)
  {
    ccd_frame_slots[(uint32_t)active_slot].ready = 0U;
    ccd_frame_slots[(uint32_t)active_slot].flags |= fault_flags;
    ccd_frame_slots[(uint32_t)active_slot].packet.header.flags = ccd_frame_slots[(uint32_t)active_slot].flags;
  }

  ccd_active_slot = -1;
}

static void ArmFrameCapture(void)
{
  int32_t slot_index;
  uint32_t frame_id = ++ccd_icg_cycle_counter;

  if (ccd_active_slot >= 0)
  {
    ccd_dropped_frame_count++;
    AbortActiveCapture(CCD_FRAME_FLAG_TIMING_FAULT);
  }

  slot_index = AcquireFrameSlot();
  if (slot_index < 0)
  {
    ccd_dropped_frame_count++;
    return;
  }

  ccd_frame_slots[(uint32_t)slot_index].ready = 0U;
  ccd_frame_slots[(uint32_t)slot_index].flags = CCD_FRAME_FLAG_ICG_SYNC;
  PrepareFrameHeader((uint32_t)slot_index, frame_id, ccd_frame_slots[(uint32_t)slot_index].flags);
  ccd_active_slot = (int8_t)slot_index;

  (void)HAL_ADC_Stop_DMA(&hadc1);
  __HAL_TIM_DISABLE(&htim2);
  __HAL_TIM_SET_COUNTER(&htim2, CCD_ADC_INITIAL_COUNTER);
  __HAL_TIM_CLEAR_FLAG(&htim2, TIM_FLAG_UPDATE);

  if (HAL_ADC_Start_DMA(
          &hadc1,
          (uint32_t *)ccd_frame_slots[(uint32_t)slot_index].packet.samples,
          CCD_LINE_SAMPLE_COUNT) != HAL_OK)
  {
    ccd_dropped_frame_count++;
    AbortActiveCapture(CCD_FRAME_FLAG_TIMING_FAULT);
    ccd_timing_fault = 1U;
    return;
  }

  /* TIM4 OC1REF rising starts the armed timer in hardware, not this ISR. */
}

static uint8_t SendFrameSlot(uint32_t slot_index)
{
  uint8_t status;

  ccd_frame_slots[slot_index].packet.header.flags = ccd_frame_slots[slot_index].flags;
  status = CDC_Transmit_Blocking(
      (const uint8_t *)&ccd_frame_slots[slot_index].packet,
      (uint16_t)CCD_USB_FRAME_BYTES,
      CCD_FRAME_TX_TIMEOUT_MS);
  if (status != USBD_OK)
  {
    return status;
  }

  return CDC_WaitForTxReady(CCD_FRAME_TX_TIMEOUT_MS);
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_ADC1_Init();
  MX_TIM1_Init();
  MX_USB_DEVICE_Init();
  MX_TIM2_Init();
  MX_TIM3_Init();
  MX_TIM4_Init();
  MX_TIM5_Init();
  /* USER CODE BEGIN 2 */
  HAL_Delay(200);
  SendStatusLine("USB CDC phase-preserving integration firmware v2\r\n");
  StartTiming(CCD_MIN_INTEGRATION_US);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
    PollTimingCommands();
    int32_t ready_slot = FindNextReadyFrameSlot();
    if (ready_slot >= 0)
    {
      __disable_irq();
      ccd_sending_slot = (int8_t)ready_slot;
      __enable_irq();

      if (SendFrameSlot((uint32_t)ready_slot) != USBD_OK)
      {
        ccd_usb_timeout_count++;
        ccd_frame_slots[(uint32_t)ready_slot].flags |= CCD_FRAME_FLAG_USB_TIMEOUT;
      }

      __disable_irq();
      ReleaseFrameSlot((uint32_t)ready_slot);
      ccd_sending_slot = -1;
      __enable_irq();
    }
  }
  /* USER CODE END 3 */
}

static void MX_DMA_Init(void)
{
  __HAL_RCC_DMA1_CLK_ENABLE();
  __HAL_RCC_DMA2_CLK_ENABLE();
  HAL_NVIC_SetPriority(DMA1_Stream2_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Stream2_IRQn);
  HAL_NVIC_SetPriority(DMA1_Stream6_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Stream6_IRQn);

  HAL_NVIC_SetPriority(DMA2_Stream0_IRQn, 1, 0);
  HAL_NVIC_EnableIRQ(DMA2_Stream0_IRQn);
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 25;
  RCC_OscInitStruct.PLL.PLLN = 192;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_3) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */

  /** Configure the global features of the ADC (Clock, Resolution, Data Alignment and number of conversion)
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.ScanConvMode = DISABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_RISING;
  hadc1.Init.ExternalTrigConv = ADC_EXTERNALTRIGCONV_T2_TRGO;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 1;
  hadc1.Init.DMAContinuousRequests = ENABLE;
  hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure for the selected ADC regular channel its corresponding rank in the sequencer and its sample time.
  */
  sConfig.Channel = ADC_CHANNEL_0;
  sConfig.Rank = 1;
  sConfig.SamplingTime = ADC_SAMPLETIME_15CYCLES;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief TIM1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM1_Init(void)
{

  /* USER CODE BEGIN TIM1_Init 0 */

  /* USER CODE END TIM1_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};
  TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

  /* USER CODE BEGIN TIM1_Init 1 */

  /* USER CODE END TIM1_Init 1 */
  htim1.Instance = TIM1;
  htim1.Init.Prescaler = 0;
  htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim1.Init.Period = 47;
  htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim1.Init.RepetitionCounter = 0;
  htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_Base_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim1, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_ENABLE;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 24;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCNPolarity = TIM_OCNPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
  sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
  sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
  sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
  sBreakDeadTimeConfig.DeadTime = 0;
  sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
  sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
  sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
  if (HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM1_Init 2 */

  /* USER CODE END TIM1_Init 2 */
  HAL_TIM_MspPostInit(&htim1);

}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 0;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 191;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_Base_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_UPDATE;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 96;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  if (HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */
  HAL_TIM_MspPostInit(&htim2);

}

/**
  * @brief TIM3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM3_Init(void)
{

  /* USER CODE BEGIN TIM3_Init 0 */

  /* USER CODE END TIM3_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};

  /* USER CODE BEGIN TIM3_Init 1 */

  /* USER CODE END TIM3_Init 1 */
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 47;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 959;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_Base_Init(&htim3) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim3, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim3) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 576;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  if (HAL_TIM_PWM_ConfigChannel(&htim3, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM3_Init 2 */

  /* USER CODE END TIM3_Init 2 */
  HAL_TIM_MspPostInit(&htim3);

}

/**
  * @brief TIM4 Initialization Function
  * Generates ADC trigger signal at 8ms intervals
  * @param None
  * @retval None
  */
static void MX_TIM4_Init(void)
{

  /* USER CODE BEGIN TIM4_Init 0 */

  /* USER CODE END TIM4_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};

  /* USER CODE BEGIN TIM4_Init 1 */

  /* USER CODE END TIM4_Init 1 */
  htim4.Instance = TIM4;
  htim4.Init.Prescaler = 47;
  htim4.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim4.Init.Period = 7999;
  htim4.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim4.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_Base_Init(&htim4) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim4, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim4) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_OC1REF;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim4, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM2;
  sConfigOC.Pulse = 7388;
  sConfigOC.OCPolarity = CCD_ICG_INVERT_OUTPUT ? TIM_OCPOLARITY_LOW : TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  if (HAL_TIM_PWM_ConfigChannel(&htim4, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM4_Init 2 */
  HAL_NVIC_SetPriority(TIM4_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(TIM4_IRQn);

  /* USER CODE END TIM4_Init 2 */
  HAL_TIM_MspPostInit(&htim4);

}

/**
  * @brief TIM5 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM5_Init(void)
{

  /* USER CODE BEGIN TIM5_Init 0 */

  /* USER CODE END TIM5_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM5_Init 1 */

  /* USER CODE END TIM5_Init 1 */
  htim5.Instance = TIM5;
  htim5.Init.Prescaler = 0;
  htim5.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim5.Init.Period = 191;
  htim5.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim5.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim5) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim5, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_UPDATE;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim5, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM5_Init 2 */

  /* USER CODE END TIM5_Init 2 */
}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  /* USER CODE BEGIN MX_GPIO_Init_1 */

  /* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, SH_Pin|ICG_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pins : SH_Pin ICG_Pin */
  GPIO_InitStruct.Pin = SH_Pin|ICG_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /* USER CODE BEGIN MX_GPIO_Init_2 */

  /* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *hadc)
{
  if (hadc->Instance == ADC1)
  {
    ccd_dma_half_count++;
  }
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc)
{
  if (hadc->Instance != ADC1) return;
  __HAL_TIM_DISABLE(&htim2);
  int8_t slot = ccd_active_slot;
  if (slot >= 0) {
    if (ccd_discard_exposure != 0U || ccd_timing_fault != 0U) {
      ccd_discard_exposure = 0U;
    } else {
      ccd_frame_slots[(uint32_t)slot].ready = 1U;
      if (ccd_requested_us == ccd_integration_us && ccd_requested_us != 0U)
        ccd_applied_frame_id = ccd_frame_slots[(uint32_t)slot].packet.header.frame_id;
    }
  }
  ccd_dma_full_count++;
  ccd_frame_counter++;
  ccd_active_slot = -1;
  if (ccd_arm_due != 0U) {
    ccd_arm_due = 0U;
    HandleFrameBoundary();
  }
}

void HAL_ADC_ErrorCallback(ADC_HandleTypeDef *hadc)
{
  if (hadc->Instance == ADC1) ccd_timing_fault = 1U;
}

void HAL_TIM_ErrorCallback(TIM_HandleTypeDef *htim)
{
  if (htim->Instance == TIM3 || htim->Instance == TIM4) ccd_timing_fault = 1U;
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  if (htim->Instance != TIM4 || ccd_running == 0U) return;
  /* Only the last segment wraps a physical frame; other updates are invisible. */
  ccd_segment_index = (ccd_segment_index + 1U) % ccd_segment_count;
  if (ccd_segment_index != 0U) return;
  ccd_icg_end_count++;
  __HAL_TIM_DISABLE(&htim2);
  if (ccd_active_slot >= 0) {
    /* The final DMA transfer can precede its lower-priority callback.
       Do not mistake pending ISR bookkeeping for an incomplete acquisition. */
    if (__HAL_DMA_GET_COUNTER(&hdma_adc1) == 0U) ccd_arm_due = 1U;
    else ccd_timing_fault = 1U;
    return;
  }
  HandleFrameBoundary();
}

static void HandleFrameBoundary(void)
{
  if (ccd_timing_fault != 0U) return;
  if (ccd_requested_us != 0U && ccd_requested_us != ccd_integration_us) {
    ccd_reconfigure_ready = 1U;
    return;
  }
  ArmFrameCapture();
}

void HAL_TIM_PWM_PulseFinishedCallback(TIM_HandleTypeDef *htim)
{
  if (htim->Instance == TIM4) ccd_icg_start_count++;
}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
