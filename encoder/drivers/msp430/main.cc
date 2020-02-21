// vim: ts=2:et:ft=cpp
// Copyright 2020 D. Kellermann <kellermann@protonmail.com>

#include <msp430.h>

#include <cstdint>


namespace {

  constexpr auto const EncoderA = (1U << 2U); // P1.2
  constexpr auto const EncoderB = (1U << 3U); // P1.3
  constexpr auto const EncoderS = (1U << 4U); // P1.4

  __attribute__ ((interrupt(3)))
  void port1_isr()
  {
    LPM4_EXIT;
  }

} // namespace


int main()
{
  /*
   * The state is kept on the stack as the stack memory area is present
   * anyways and we can conserve a bit of memory this way.
   */

  uint8_t old_pval = 0U;

  int volatile encoder_count = 0;
  int volatile switch_action_count = 0;

  /*
   * All logic is implemented in this loop.  Any interrupt will cause the
   * loop to be executed once.
   *   The set-up is repeated for each iteration in order to make sure
   * that sporadic issues that cause configuration errors do not persist.
   */

  while (true) {
    // setup
    {
      __disable_interrupt();

      /* TODO
       * The watchdog will make sure that the loop is executed and the system
       * re-configured in case other interrupts are prevented somehow.
       */
      WDTCTL = WDTPW | WDTHOLD;

      // unused pins should be outputs
      //      vvvvv
      P1DIR = 0xffU & ~(EncoderA | EncoderB | EncoderS);
      P2DIR = 0xffU;

      // FIXME pval must be initially read at this point; subsequently it
      // will be read by the logic
      old_pval = P1IN;

      // trigger interrupts on next edge depending on last processed state
      P1IES = old_pval & (EncoderA | EncoderS);

      P1IE = EncoderA | EncoderS;

      P1IFG &= P1IE; // clear all unused interrupt flags
      __enable_interrupt();
    }

    // enter LPM and wait for interrupts
    LPM4;

    {
      auto const new_pval = P1IN;
      auto const pval_diff = old_pval ^ new_pval;

      if (pval_diff & (EncoderA | EncoderB)) {
        if ((old_pval & EncoderA) == (new_pval & EncoderB)) {
          --encoder_count;
        }
        else {
          ++encoder_count;
        }
      }

      if (pval_diff & EncoderS) {
        ++switch_action_count;
      }

      old_pval = new_pval;
    }
  }
}
