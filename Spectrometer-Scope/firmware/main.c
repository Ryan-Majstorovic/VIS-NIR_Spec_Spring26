#define CCD_SCOPE_DIAGNOSTIC 1
/* Separate scope application; reuse production drive generation and vendor USB.
 * Digital samples are reads of real MCU GPIO input registers, NOT synthesized
 * timer diagrams. Detector polarity is a separate, explicit board assumption.
 * ADC DMA is deliberately extended and TIM4 acquisition interrupts suppressed.
 */
#include "main.h"
#include <stdint.h>

static HAL_StatusTypeDef ScopeAdcStart(ADC_HandleTypeDef *, uint32_t *, uint32_t);
#define main production_main_unused
#define CCD_ReceiveCommandBytes ProductionReceiveUnused
#define HAL_ADC_Start_DMA ScopeAdcStart
#define HAL_ADC_ConvCpltCallback ProductionAdcCompleteUnused
#define HAL_ADC_ConvHalfCpltCallback ProductionAdcHalfUnused
#define HAL_ADC_ErrorCallback ProductionAdcErrorUnused
#include "../../CCD-Driver-Code/STM32F411_Basic/Core/Src/main.c"
#undef main
#undef CCD_ReceiveCommandBytes
#undef HAL_ADC_Start_DMA
#undef HAL_ADC_ConvCpltCallback
#undef HAL_ADC_ConvHalfCpltCallback
#undef HAL_ADC_ErrorCallback
extern USBD_HandleTypeDef hUsbDeviceFS;

#define LOGIC_CAPACITY 6144U
#define ADC_CAPACITY 12000U
#define SCOPE_MAGIC 0x50435343UL /* CSCP */
#define SCOPE_FIELDS 48U
typedef struct { uint32_t cycles; uint32_t ports; } LogicSample;
typedef struct {
  uint32_t magic;
  uint16_t version;
  uint16_t header_bytes;
  uint32_t field[SCOPE_FIELDS];
} ScopeHeader;
_Static_assert(sizeof(ScopeHeader) == 200U, "Scope header wire layout");
static LogicSample logic_samples[LOGIC_CAPACITY];
static uint16_t analog_samples[ADC_CAPACITY];
static volatile uint32_t scope_adc_complete, scope_adc_errors;
static volatile uint32_t scope_adc_done_cycles, scope_adc_done_phase;
static uint32_t scope_adc_target = 4000U;
static volatile uint32_t scope_command; /* 1/2 legacy, 3/4 fast, 5 slow lead-in */
static volatile uint32_t scope_rx_used;
static volatile uint8_t scope_rx_discard;
static char scope_rx_line[32];
static uint32_t scope_capture_id;

void ScopeDmaIrqBegin(void)
{
  if (DMA2->LISR & DMA_LISR_TCIF0) {
    TIM2->CR1 &= ~TIM_CR1_CEN;
    ADC1->CR2 &= ~(ADC_CR2_EXTEN | ADC_CR2_ADON);
    scope_adc_done_cycles = DWT->CYCCNT;
    scope_adc_done_phase = TIM4->CNT;
    if (ADC1->SR & ADC_SR_OVR) scope_adc_errors |= HAL_ADC_ERROR_OVR;
  }
}

void ADC_IRQHandler(void)
{
  /* A real overrun while DMA still expects data invalidates the acquisition. */
  if (ADC1->SR & ADC_SR_OVR) {
    scope_adc_errors |= HAL_ADC_ERROR_OVR;
    TIM2->CR1 &= ~TIM_CR1_CEN;
    ADC1->CR2 &= ~(ADC_CR2_EXTEN | ADC_CR2_ADON);
  }
  HAL_ADC_IRQHandler(&hadc1);
}

static HAL_StatusTypeDef ScopeAdcStart(ADC_HandleTypeDef *adc, uint32_t *unused, uint32_t count)
{
  (void)unused; (void)count;
  ADC1->CR2 = (ADC1->CR2 & ~(ADC_CR2_EXTEN | ADC_CR2_CONT)) | ADC_EXTERNALTRIGCONVEDGE_RISING;
  if (TIM2->CNT > TIM2->ARR) TIM2->CNT = TIM2->ARR + 1U - 48U;
  return HAL_ADC_Start_DMA(adc, (uint32_t *)analog_samples, scope_adc_target);
}

void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef *adc) { (void)adc; }
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *adc)
{
  if (adc->Instance == ADC1) {
    TIM2->CR1 &= ~TIM_CR1_CEN; scope_adc_complete = 1U;
  }
}
void HAL_ADC_ErrorCallback(ADC_HandleTypeDef *adc)
{
  if (adc->Instance == ADC1) scope_adc_errors |= HAL_ADC_GetError(adc);
}

void CCD_ReceiveCommandBytes(const uint8_t *bytes, uint32_t length)
{
  for (uint32_t i = 0U; i < length; ++i) {
    char c = (char)bytes[i];
    if (c == '\r') continue;
    if (c != '\n') {
      if (scope_rx_used + 1U < sizeof(scope_rx_line)) scope_rx_line[scope_rx_used++] = c;
      else scope_rx_discard = 1U;
    } else {
      scope_rx_line[scope_rx_used] = 0;
      if (!scope_rx_discard && !scope_command) {
        if (strcmp(scope_rx_line, "SCOPE ZOOM") == 0) scope_command = 1U;
        if (strcmp(scope_rx_line, "SCOPE OVERVIEW") == 0) scope_command = 2U;
        if (strcmp(scope_rx_line, "SCOPE FAST") == 0) scope_command = 3U;
        if (strcmp(scope_rx_line, "SCOPE FASTOVERVIEW") == 0) scope_command = 4U;
        if (strcmp(scope_rx_line, "SCOPE SLOW") == 0) scope_command = 5U;
        if (strcmp(scope_rx_line, "SCOPE CORRECTED") == 0) scope_command = 6U;
        if (strcmp(scope_rx_line, "SCOPE CORRECTEDOVERVIEW") == 0) scope_command = 7U;
        if (strcmp(scope_rx_line, "SCOPE EXPOSED") == 0) scope_command = 8U;
        if (strcmp(scope_rx_line, "SCOPE EXPOSEDOVERVIEW") == 0) scope_command = 9U;
      }
      scope_rx_used = 0U; scope_rx_discard = 0U;
    }
  }
}

static uint32_t CrcUpdate(uint32_t crc, const void *data, uint32_t length)
{
  const uint8_t *p = data;
  while (length--) {
    crc ^= *p++;
    for (uint32_t bit = 0; bit < 8; ++bit) crc = (crc >> 1) ^ (0xEDB88320UL & (0U - (crc & 1U)));
  }
  return crc;
}

static uint8_t SendBytes(const void *data, uint32_t length)
{
  const uint8_t *p = data;
  while (length) {
    uint32_t count = length > 1024U ? 1024U : length;
    uint32_t began = HAL_GetTick();
    while (!CDC_TxReady_FS()) {
      if (hUsbDeviceFS.dev_state != USBD_STATE_CONFIGURED || HAL_GetTick() - began > 2000U) return 0U;
    }
    if (CDC_Transmit_FS((uint8_t *)p, (uint16_t)count) != USBD_OK) return 0U;
    began = HAL_GetTick();
    while (!CDC_TxReady_FS()) {
      if (hUsbDeviceFS.dev_state != USBD_STATE_CONFIGURED || HAL_GetTick() - began > 2000U) return 0U;
    }
    p += count; length -= count;
  }
  return 1U;
}

static void Capture(uint32_t mode)
{
  ScopeHeader header = {SCOPE_MAGIC, 2U, sizeof(ScopeHeader), {0}};
  uint32_t corrected = mode >= 6U;
  uint32_t integration = mode >= 8U ? 100U : 10U;
  uint32_t fast = mode == 3U || mode == 4U || corrected;
  uint32_t leadin = mode >= 3U;
  uint32_t overview = mode == 2U || mode == 4U || mode == 7U || mode == 9U;
  StopTiming();
  scope_adc_target = fast ? 12000U : (leadin ? 4500U : 4000U);
  /* 24 MHz ADC, 12 bits + 3 sample cycles + 2 trigger-latency cycles.
     72 CPU cycles (750 ns) also allow the extra APB2 synchronization cycle.
     Keep all CCD drive clocks unchanged; only the diagnostic sampling changes. */
  TIM2->ARR = fast ? 71U : 191U;
  TIM2->CCR1 = fast ? 36U : 96U;
  ADC1->SMPR2 = (ADC1->SMPR2 & ~ADC_SMPR2_SMP0) | (fast ? 0U : ADC_SAMPLETIME_15CYCLES);
  scope_adc_complete = 0U; scope_adc_errors = 0U;
  StartTiming(integration);
  /* Optional diagnostic comparison: ICG rises at 8 us, after SH falls at
     6.5 us. The 7992-us high interval still covers the complete 7388-us line.
     CCR1 is preloaded, so the change takes effect at the observed next wrap. */
  TIM4->CCR1 = corrected ? 16U : 1224U; /* Preserve the explicit legacy comparison. */
  /* Observe the next complete timing cycle; do not let the production frame ISR
     stop/rearm this intentionally longer DMA transfer. The drive PWMs continue. */
  TIM4->DIER = 0U;
  HAL_NVIC_DisableIRQ(TIM4_IRQn);
  uint32_t timeout = HAL_GetTick();
  while (TIM4->CNT < 15200U) { if (HAL_GetTick() - timeout > 30U) return; }
  /* Arm a fresh analog trace before the next wrap. Its first conversion is
     triggered by that cycle's ICG OC1REF rising edge, inside the logic trace. */
  (void)HAL_ADC_Stop_DMA(&hadc1);
  TIM2->CR1 &= ~TIM_CR1_CEN;
  uint32_t initial_counter = TIM2->ARR + 1U - 48U;
  /* A spare internal compare starts acquisition 200 us before frame wrap.
     OC2 is not connected to a pin. ICG/SH/phiM waveforms are unchanged. */
  TIM4->CR2 = TIM_TRGO_RESET;
  if (leadin) {
    TIM4->CCMR1 = (TIM4->CCMR1 & ~(TIM_CCMR1_OC2M | TIM_CCMR1_CC2S | TIM_CCMR1_OC2PE)) |
                     (TIM_OCMODE_PWM2 << 8);
    TIM4->CCR2 = 15600U;
    TIM4->CR2 = TIM_TRGO_OC2REF;
  } else TIM4->CR2 = TIM_TRGO_OC1REF;
  TIM2->CNT = initial_counter;
  TIM2->SR = 0U;
  scope_adc_complete = 0U; scope_adc_errors = 0U;
  scope_adc_done_cycles = 0U; scope_adc_done_phase = 0U;
  if (ScopeAdcStart(&hadc1, NULL, 0U) != HAL_OK) return;

  /* Both port reads precede the cycle timestamp. Their sequential read skew is
     not subtracted: the host includes the observed sample gap in uncertainty. */
  uint32_t mask = __get_PRIMASK();
  if (!overview) __disable_irq();
  uint32_t origin = DWT->CYCCNT;
  uint32_t phase = TIM4->CNT;
  uint32_t due = origin;
  uint32_t stride = overview ? 168U : 0U; /* Overview: nominal 1.75 us, > full frame. */
  for (uint32_t i = 0; i < LOGIC_CAPACITY; ++i) {
    if (stride) while ((int32_t)(DWT->CYCCNT - due) < 0) { }
    uint32_t pa = GPIOA->IDR;
    uint32_t pb = GPIOB->IDR;
    logic_samples[i].cycles = DWT->CYCCNT - origin;
    logic_samples[i].ports = (pa & 0xffffU) | (pb << 16);
    due += stride;
  }
  __set_PRIMASK(mask);
  timeout = HAL_GetTick();
  /* The complete interrupt may have been pending during the digital trace. */
  while (!scope_adc_complete && !scope_adc_errors && HAL_GetTick() - timeout < 50U) { }
  uint32_t remaining = __HAL_DMA_GET_COUNTER(&hdma_adc1);
  uint32_t adc_sr = ADC1->SR, adc_cr2 = ADC1->CR2;
  (void)HAL_ADC_Stop_DMA(&hadc1);
  TIM2->CR1 &= ~TIM_CR1_CEN;

  uint32_t *f = header.field;
  f[0] = ++scope_capture_id; f[1] = HAL_RCC_GetHCLKFreq();
  f[2] = LOGIC_CAPACITY; f[3] = scope_adc_target - remaining;
  f[4] = sizeof(LogicSample); f[5] = 48U;
  f[6] = origin; f[7] = stride; f[8] = 768000U; f[9] = integration;
  f[10] = 1U; /* PA8 phiM, PA6 SH, PB6 ICG, PA5 ADC clock. */
  f[11] = 7U; /* Expected board inversion: phiM/SH/ICG. Inferred, not sensed. */
  f[12] = scope_adc_complete ? 1U : 0U; f[13] = remaining; f[14] = scope_adc_errors;
  f[15] = TIM1->PSC; f[16] = TIM1->ARR; f[17] = TIM1->CCR1;
  f[18] = TIM2->PSC; f[19] = TIM2->ARR;
  f[20] = TIM3->PSC; f[21] = TIM3->ARR; f[22] = TIM3->CCR1;
  f[23] = TIM4->PSC; f[24] = TIM4->ARR; f[25] = TIM4->CCR1;
  f[26] = phase; f[27] = mode;
  f[28] = TIM2->SMCR; f[29] = TIM3->CCER; f[30] = TIM4->CCER;
  f[31] = 0x00020000U;
  f[32] = scope_adc_target; f[33] = HAL_RCC_GetPCLK2Freq() / 4U;
  f[34] = fast ? 3U : 15U; f[35] = 12U;
  f[36] = leadin ? (uint32_t)(-19200 + 48) : TIM4->CCR1 * 48U + 48U;
  f[37] = ADC1->CR1; f[38] = adc_cr2; f[39] = ADC1->SMPR2;
  f[40] = TIM4->CR2; f[41] = TIM4->CCR2;
  f[42] = scope_adc_complete ? scope_adc_done_cycles - origin : 0U;
  f[43] = scope_adc_done_phase; f[44] = adc_sr; f[45] = HAL_DMA_GetError(&hdma_adc1);
  f[46] = initial_counter;
  uint32_t crc = CrcUpdate(0xffffffffU, &header, sizeof(header));
  crc = CrcUpdate(crc, logic_samples, sizeof(logic_samples));
  crc = CrcUpdate(crc, analog_samples, f[3] * sizeof(uint16_t)) ^ 0xffffffffU;
  if (!SendBytes(&header, sizeof(header))) return;
  if (!SendBytes(logic_samples, sizeof(logic_samples))) return;
  if (!SendBytes(analog_samples, f[3] * sizeof(uint16_t))) return;
  (void)SendBytes(&crc, sizeof(crc));
}

int main(void)
{
  HAL_Init(); SystemClock_Config();
  MX_GPIO_Init(); MX_DMA_Init(); MX_TIM1_Init(); MX_TIM2_Init(); MX_TIM3_Init(); MX_TIM4_Init(); MX_ADC1_Init();
  HAL_NVIC_SetPriority(DMA2_Stream0_IRQn, 0U, 0U);
  HAL_NVIC_SetPriority(ADC_IRQn, 0U, 0U); HAL_NVIC_EnableIRQ(ADC_IRQn);
  CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
  DWT->CYCCNT = 0U; DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
  MX_USB_DEVICE_Init();
  StartTiming(10U); TIM4->DIER = 0U; HAL_NVIC_DisableIRQ(TIM4_IRQn);
  while (1) {
    if (scope_command && hUsbDeviceFS.dev_state == USBD_STATE_CONFIGURED) {
      uint32_t command = scope_command; scope_command = 0U;
      Capture(command);
    }
  }
}
