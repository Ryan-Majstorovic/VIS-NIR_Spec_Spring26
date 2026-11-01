#ifndef CCD_TIMING_H
#define CCD_TIMING_H

#include <stdint.h>

#define CCD_MIN_INTEGRATION_US 10U
#define CCD_BASE_FRAME_US 8000U
#define CCD_MAX_INTEGRATION_US 5000000U
#define CCD_READOUT_US 7388U
#define CCD_MAX_SEGMENT_US 32000U
#define CCD_MAX_SEGMENTS ((CCD_MAX_INTEGRATION_US + CCD_MAX_SEGMENT_US - 1U) / CCD_MAX_SEGMENT_US)
#define CCD_TIMER_PRESCALER 47U /* 96 MHz / (47 + 1) = 2 MHz. */
#define CCD_ADC_INITIAL_COUNTER 144U /* (192 - 144) / 96 MHz = first trigger after 0.5 us. */
#define CCD_MASTER_INITIAL_COUNTER 12U /* Scope-verify propagation margin inside phiM high. */
#define CCD_SH_HIGH_TICKS 12U /* 6 us at 2 MHz; never stretched for phase correction. */

typedef struct {
  uint32_t arr;
  uint32_t reserved; /* DMA burst crosses the unused TIM3/TIM4 RCR address. */
  uint32_t ccr;
} CcdTimingSegment;

static inline uint8_t CcdIntegrationValid(uint32_t us)
{
  return us >= CCD_MIN_INTEGRATION_US && us <= CCD_MAX_INTEGRATION_US &&
      (us > CCD_BASE_FRAME_US || CCD_BASE_FRAME_US % us == 0U);
}

static inline uint32_t CcdSegmentCount(uint32_t us)
{
  return (us + CCD_MAX_SEGMENT_US - 1U) / CCD_MAX_SEGMENT_US;
}

static inline CcdTimingSegment CcdSegment(uint32_t us, uint32_t index, uint8_t sh)
{
  uint32_t n = CcdSegmentCount(us);
  uint32_t duration = us / n + (index < us % n ? 1U : 0U);
  CcdTimingSegment segment = {duration * 2U - 1U, 0U, 0U};
  if (sh != 0U) {
    segment.ccr = index == 0U ? CCD_SH_HIGH_TICKS : 0U;
  } else {
    /* PWM2 remains low when compare exceeds ARR; only the final segment reads out. */
    segment.ccr = index + 1U == n ? (duration - CCD_READOUT_US) * 2U : duration * 2U;
  }
  return segment;
}

#endif
