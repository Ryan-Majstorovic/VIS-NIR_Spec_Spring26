/* CSCP v2 observer of the running production clocks and production ADC frame.
 * Zoom masks interrupts only during the short digital observation (< readout).
 * Hardware PWM/ADC/DMA continue; overview leaves interrupts enabled.
 * Sensor-side polarity and propagation remain external verification items.
 */
#define PROD_LOGIC_COUNT 6144U
typedef struct { uint32_t cycles, ports; } ProductionLogicSample;
static ProductionLogicSample production_logic[PROD_LOGIC_COUNT];

/* Fixed observation loop in SRAM avoids flash/cache stalls at a 250 ns
   master-clock half period. DWT timestamps still bound actual resolution. */
__attribute__((section(".RamFunc"), noinline))
static void ProductionLogicZoom(uint32_t origin)
{
  ProductionLogicSample *out = production_logic;
  ProductionLogicSample *end = out + PROD_LOGIC_COUNT;
  uint32_t a, b, t;
  __asm volatile (
      "1: ldr %[a], [%[pa]]\n"
      "ldr %[b], [%[pb]]\n"
      "ldr %[t], [%[dwt]]\n"
      "uxth %[a], %[a]\n"
      "orr %[a], %[a], %[b], lsl #16\n"
      "sub %[t], %[t], %[origin]\n"
      "strd %[t], %[a], [%[out]], #8\n"
      "cmp %[out], %[end]\n"
      "bne 1b\n"
      : [out] "+r" (out), [a] "=&r" (a), [b] "=&r" (b), [t] "=&r" (t)
      : [pa] "r" (&GPIOA->IDR), [pb] "r" (&GPIOB->IDR),
        [dwt] "r" (&DWT->CYCCNT), [origin] "r" (origin), [end] "r" (end)
      : "cc", "memory");
}

static uint8_t ProductionScopeSend(const void *data, uint32_t length)
{
  const uint8_t *p = data;
  while (length) {
    uint16_t n = length > 1024U ? 1024U : (uint16_t)length;
    if (CDC_WaitForTxReady(100U) != USBD_OK ||
        CDC_Transmit_Blocking(p, n, 100U) != USBD_OK ||
        CDC_WaitForTxReady(100U) != USBD_OK) return 0U;
    p += n; length -= n;
  }
  return 1U;
}

static void ProductionScopeCapture(uint32_t mode)
{
  struct { uint32_t magic; uint16_t version, bytes; uint32_t f[48]; }
      header = {0x50435343UL, 2U, 200U, {0}};
  uint32_t began = HAL_GetTick();
  /* Start 400 us before a physical frame, after the preceding readout. */
  while (!(ccd_segment_index + 1U == ccd_segment_count &&
           TIM4->CNT >= TIM4->ARR - 800U && TIM4->CNT < TIM4->ARR - 600U)) {
    /* Scope acquisition temporarily owns transport; free older queued frames
       so the selected upcoming frame can be acquired even at long exposures. */
    for (uint32_t i = 0U; i < CCD_FRAME_BUFFER_COUNT; ++i)
      if (ccd_frame_slots[i].ready && (int8_t)i != ccd_active_slot && (int8_t)i != ccd_sending_slot) ReleaseFrameSlot(i);
    PollCaptureArm();
    if (ccd_timing_fault || HAL_GetTick() - began > ccd_integration_us / 1000U + 100U) {
      SendStatusLine("ERR SCOPE WAIT\r\n"); return;
    }
  }
  PollCaptureArm();
  if (ccd_active_slot < 0) { SendStatusLine("ERR SCOPE NO BUFFER\r\n"); return; }
  uint32_t slot = (uint32_t)ccd_active_slot;
  uint32_t target = ccd_frame_slots[slot].packet.header.frame_id;
  ccd_scope_hold = 1U; /* Hold this completed frame while the scope response is sent. */
  uint32_t stride = mode == 11U ? 168U : 0U;
  uint32_t mask = __get_PRIMASK();
  if (!stride) __disable_irq();
  uint32_t origin = DWT->CYCCNT, phase = TIM4->CNT, due = origin;
  if (!stride) ProductionLogicZoom(origin);
  else for (uint32_t i = 0U; i < PROD_LOGIC_COUNT; ++i) {
    while ((int32_t)(DWT->CYCCNT - due) < 0) { }
    uint32_t pa = GPIOA->IDR, pb = GPIOB->IDR;
    production_logic[i].cycles = DWT->CYCCNT - origin;
    production_logic[i].ports = (pa & 0xffffU) | (pb << 16);
    due += stride;
  }
  __set_PRIMASK(mask);
  began = HAL_GetTick();
  while (ccd_active_slot >= 0 && !ccd_timing_fault && HAL_GetTick() - began < 30U) { }
  uint32_t *f = header.f;
  f[0] = target; f[1] = HAL_RCC_GetHCLKFreq();
  f[2] = PROD_LOGIC_COUNT; f[3] = CCD_LINE_SAMPLE_COUNT - __HAL_DMA_GET_COUNTER(&hdma_adc1);
  f[4] = 8U; f[5] = CCD_ADC_PERIOD_TICKS - CCD_ADC_INITIAL_COUNTER; f[6] = origin; f[7] = stride;
  f[8] = (ccd_integration_us > CCD_BASE_FRAME_US ? ccd_integration_us : CCD_BASE_FRAME_US) * 96U;
  f[9] = ccd_integration_us; f[10] = 1U; f[11] = 7U;
  f[12] = ccd_frame_slots[slot].ready && !ccd_timing_fault ? 1U : 0U;
  /* CSCP flags bit 1 records the internal trigger configuration at capture. */
  if ((TIM2->CCER & TIM_CCER_CC1E) == 0U && (GPIOA->MODER & GPIO_MODER_MODER5) == GPIO_MODER_MODER5)
    f[12] |= 2U;
  f[13] = __HAL_DMA_GET_COUNTER(&hdma_adc1); f[14] = HAL_ADC_GetError(&hadc1) | (ccd_timing_fault ? 0x80000000U : 0U);
  f[15] = TIM1->PSC; f[16] = TIM1->ARR; f[17] = TIM1->CCR1;
  f[18] = TIM2->PSC; f[19] = TIM2->ARR;
  f[20] = TIM3->PSC; f[21] = TIM3->ARR; f[22] = TIM3->CCR1;
  f[23] = TIM4->PSC; f[24] = TIM4->ARR; f[25] = CCD_ICG_LOW_US * 2U;
  f[26] = phase; f[27] = mode;
  f[28] = TIM2->SMCR; f[29] = TIM3->CCER; f[30] = TIM4->CCER;
  f[31] = CCD_TIMING_PROFILE_ID;
  f[32] = CCD_LINE_SAMPLE_COUNT; f[33] = HAL_RCC_GetPCLK2Freq() / 4U;
  f[34] = 15U; f[35] = 12U; f[36] = CCD_ICG_LOW_US * 96U + f[5];
  f[37] = ADC1->CR1; f[38] = ADC1->CR2; f[39] = ADC1->SMPR2;
  f[40] = TIM4->CR2; f[41] = TIM4->CCR2;
  f[42] = ccd_adc_done_cycles - origin; f[43] = ccd_adc_done_phase;
  f[44] = ccd_adc_status; f[45] = HAL_DMA_GetError(&hdma_adc1);
  f[46] = CCD_ADC_INITIAL_COUNTER;
  uint32_t crc = CcdCrcUpdate(0xffffffffU, &header, sizeof(header));
  crc = CcdCrcUpdate(crc, production_logic, sizeof(production_logic));
  crc = CcdCrcUpdate(crc, ccd_frame_slots[slot].packet.samples, f[3] * 2U) ^ 0xffffffffU;
  if (ProductionScopeSend(&header, sizeof(header)) &&
      ProductionScopeSend(production_logic, sizeof(production_logic)) &&
      ProductionScopeSend(ccd_frame_slots[slot].packet.samples, f[3] * 2U))
    (void)ProductionScopeSend(&crc, sizeof(crc));
  ccd_scope_hold = 0U;
}
