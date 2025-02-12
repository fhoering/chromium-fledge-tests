# Copyright 2021 RTBHOUSE. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

import logging

from common.base_test import BaseTest
from common.mockserver import MockServer
from common.utils import print_debug, measure_time, log_exception, MeasureDuration, pretty_json,\
    average_benchmarks, extract_rtbh_test_stats

logger = logging.getLogger(__file__)


class WebassemblyTest(BaseTest):

    @print_debug
    @measure_time
    @log_exception
    @average_benchmarks
    def test__basic_webassembly(self):
        with MockServer(port=9021, directory='resources/buyer') as buyer_server,\
                MockServer(port=9022, directory='resources/seller') as seller_server:

            with MeasureDuration("joinAdInterestGroup"):
                self.driver.get(buyer_server.address)
                self.assertDriverContainsText('body', 'joined interest group')

            with MeasureDuration("runAdAuction"):
                self.driver.get(seller_server.address)
                self.findFrameAndSwitchToIt()
                self.assertDriverContainsText('body', 'TC AD')

        report_result_signals = seller_server.get_last_request("/reportResult").get_first_json_param('signals')
        logger.info(f"reportResult() signals: {pretty_json(report_result_signals)}")

        report_win_signals = buyer_server.get_last_request("/reportWin").get_first_json_param('signals')
        logger.info(f"reportWin() signals: {pretty_json(report_win_signals)}")

        # to be able to measure bidding worklet time you should use custom-built version of chromium
        # with a patch like this: https://github.com/RTBHOUSE/chromium/commits/rtb_wasm
        if 'bid_duration' in report_result_signals.get('browserSignals'):
            bid_duration_ms = int(report_result_signals.get('browserSignals').get('bid_duration')) / 1000
            logger.info(f"generateBid took: {bid_duration_ms} ms")

        return extract_rtbh_test_stats(report_result_signals)
