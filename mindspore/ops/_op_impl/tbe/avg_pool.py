# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

"""AvgPool op"""
from mindspore.ops.op_info_register import op_info_register, TBERegOp, DataType

avg_pool_op_info = TBERegOp("AvgPool") \
    .fusion_type("OPAQUE") \
    .async_flag(False) \
    .binfile_name("avg_pool.so") \
    .compute_cost(10) \
    .kernel_name("avg_pool") \
    .partial_flag(True) \
    .attr("ksize", "required", "listInt", "all") \
    .attr("strides", "required", "listInt", "all") \
    .attr("padding", "required", "str", "all") \
    .attr("data_format", "optional", "str", "all") \
    .input(0, "x", False, "required", "all") \
    .output(0, "y", False, "required", "all") \
    .dtype_format(DataType.F16_5HD, DataType.F16_5HD) \
    .get_op_info()


@op_info_register(avg_pool_op_info)
def _avg_pool_tbe():
    """AvgPool TBE register"""
    return
