TIM2 ADC Trigger Details
============================

UUID: ``3C47779C-63B3-4C7D-A690-C41F7C042E70``

TIM2 provides the 500 kHz ADC trigger timing through TRGO and a monitor output
on PA5. The firmware enables TIM2 during an ICG-synchronized capture and
disables it when DMA completes or the TIM4 compare callback marks the ICG end.





