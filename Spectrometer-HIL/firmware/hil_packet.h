#ifndef HIL_PACKET_H
#define HIL_PACKET_H

#include <stdint.h>
#include "hil_config.h"

/* Compatibility with the current CCD1 implementation, not an approved ICD. */
#define HIL_SAMPLE_COUNT 3694U
#define HIL_EFFECTIVE_START 32U
#define HIL_EFFECTIVE_COUNT 3648U

typedef struct __attribute__((packed))
{
  uint8_t magic[4];
  uint8_t version;
  uint8_t packet_type;
  uint16_t reserved;
  uint32_t frame_id;
  uint16_t sample_count;
  uint16_t effective_start;
  uint16_t effective_count;
  uint16_t flags;
  uint32_t payload_bytes;
} HilHeader;

typedef struct
{
  HilHeader header;
  uint16_t samples[HIL_SAMPLE_COUNT];
} HilPacket;

_Static_assert(sizeof(HilHeader) == 24U, "CCD1 header layout changed");
_Static_assert(sizeof(HilPacket) == 7412U, "CCD1 packet layout changed");

extern const HilPacket hil_frames[HIL_FRAME_COUNT];

#endif
