#define CCD_SCOPE_DIAGNOSTIC 1
/* Keep the vendor/production handlers, but stop ADC triggering at DMA IRQ entry,
 * before the HAL dispatch latency can generate conversions past the buffer. */
#define DMA2_Stream0_IRQHandler ProductionDmaIrqUnused
#include "../../CCD-Driver-Code/STM32F411_Basic/Core/Src/stm32f4xx_it.c"
#undef DMA2_Stream0_IRQHandler
extern void ScopeDmaIrqBegin(void);
void DMA2_Stream0_IRQHandler(void)
{
  ScopeDmaIrqBegin();
  HAL_DMA_IRQHandler(&hdma_adc1);
}
