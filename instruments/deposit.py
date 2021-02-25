# Copyright © 2017 Ondrej Martinsky, All rights reserved
# http://github.com/omartinsky/pybor
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from instruments.base_instrument import *


class Deposit(Instrument):
    @staticmethod
    def CreateFromDataFrameRow(name, eval_date, row):
        fcastL, fcastR, discL, discR, convL, convR, start, length = get_dataframe_row_cells(row)
        assert_is_set([fcastL, convL])
        assert_is_not_set([fcastR, discL, discR, convR])
        return Deposit(name,
                       curve_forecast=fcastL,
                       trade_date=eval_date,
                       start=start,
                       length=Tenor(length),
                       convention=global_conventions.get(convL))

    def __init__(self, name:str, curve_forecast:str, trade_date:int, start, length, convention):
        super().__init__(name)
        self.curve_forecast_ = curve_forecast
        self.start_ = create_date(start, trade_date)
        self.end_ = date_step(self.start_, length)
        self.accruals_ = np.array([self.start_, self.end_])
        self.dcf_ = calculate_dcfs(self.accruals_, convention.dcc)[0]

    def get_pillar_date(self):
        return self.end_

    def calc_par_rate(self, curvemap):
        curve = curvemap[self.curve_forecast_]
        df = curve.get_df(self.accruals_)
        return (df[0] / df[1] - 1) / self.dcf_
