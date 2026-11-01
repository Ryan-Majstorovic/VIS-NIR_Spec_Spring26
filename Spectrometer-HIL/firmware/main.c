/* Standalone stimulus firmware. Reuses the production project's USB stack.
 * Clock values match STM32F411_Basic (25 MHz HSE, 96 MHz CPU, 48 MHz USB).
 * No CCD clocks, ADC, acquisition DMA, or production command emulation run.
 */
#include "main.h"
#include "usb_device.h"
#include "usbd_cdc_if.h"
#include "hil_packet.h"

extern USBD_HandleTypeDef hUsbDeviceFS;
extern PCD_HandleTypeDef hpcd_USB_OTG_FS;

static HilPacket tx_packet;

void SystemClock_Config(void)
{
  RCC_OscInitTypeDef osc = {0};
  RCC_ClkInitTypeDef clocks = {0};

  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);
  osc.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  osc.HSEState = RCC_HSE_ON;
  osc.PLL.PLLState = RCC_PLL_ON;
  osc.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  /* 25 MHz / 25 * 192 / 2 = 96 MHz; PLLQ=4 gives USB its 48 MHz. */
  osc.PLL.PLLM = 25;
  osc.PLL.PLLN = 192;
  osc.PLL.PLLP = RCC_PLLP_DIV2;
  osc.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&osc) != HAL_OK)
    Error_Handler();

  clocks.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK |
                    RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
  clocks.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  clocks.AHBCLKDivider = RCC_SYSCLK_DIV1;
  clocks.APB1CLKDivider = RCC_HCLK_DIV2;
  clocks.APB2CLKDivider = RCC_HCLK_DIV1;
  if (HAL_RCC_ClockConfig(&clocks, FLASH_LATENCY_3) != HAL_OK)
    Error_Handler();
}

void HAL_MspInit(void)
{
  __HAL_RCC_SYSCFG_CLK_ENABLE();
  __HAL_RCC_PWR_CLK_ENABLE();
}

void SysTick_Handler(void)
{
  HAL_IncTick();
}

void OTG_FS_IRQHandler(void)
{
  HAL_PCD_IRQHandler(&hpcd_USB_OTG_FS);
}

void Error_Handler(void)
{
  __disable_irq();
  while (1) { }
}

int main(void)
{
  HAL_Init();
  SystemClock_Config();
  MX_USB_DEVICE_Init();

  uint32_t deadline = HAL_GetTick();
  uint32_t frame_id = 0;
  while (1)
  {
    uint32_t now = HAL_GetTick();
    if (hUsbDeviceFS.dev_state != USBD_STATE_CONFIGURED)
    {
      deadline = now;
      continue;
    }
    if ((int32_t)(now - deadline) < 0)
      continue;

    /* Count scheduled opportunities, including missed ones; never burst a
     * backlog. Unsigned subtraction also handles the HAL tick rollover. */
    uint32_t opportunities = (now - deadline) / HIL_PERIOD_MS + 1U;
    deadline += opportunities * HIL_PERIOD_MS;
    frame_id += opportunities;
#if HIL_DROP_EVERY > 0
    if (frame_id % HIL_DROP_EVERY == 0U)
      continue;
#endif

    /* CDC holds a pointer into this buffer until completion. A busy transfer
     * keeps ownership, even if it takes longer than one frame interval. */
    if (CDC_TxReady_FS() == 0U)
      continue;
    tx_packet = hil_frames[(frame_id - 1U) % HIL_FRAME_COUNT];
    tx_packet.header.frame_id = frame_id;

    /* Recheck under a short critical section: a USB reset may deinitialize
     * pClassData between the initial readiness check and this submission. */
    uint32_t interrupt_mask = __get_PRIMASK();
    __disable_irq();
    if (hUsbDeviceFS.dev_state == USBD_STATE_CONFIGURED &&
        CDC_TxReady_FS() != 0U)
    {
      (void)CDC_Transmit_FS((uint8_t *)&tx_packet, sizeof(tx_packet));
    }
    __set_PRIMASK(interrupt_mask);
  }
}
