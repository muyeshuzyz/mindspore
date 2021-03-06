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

"""__init__"""

from .add import _add_akg
from .batchmatmul import _batchmatmul_akg
from .cast import _cast_akg
from .expand_dims import _expand_dims_akg
from .greater import _greater_akg
from .inplace_assign import _inplace_assign_akg
from .maximum import _maximum_akg
from .minimum import _minimum_akg
from .mul import _mul_akg
from .real_div import _real_div_akg
from .rsqrt import _rsqrt_akg
from .select import _select_akg
from .sqrt import _sqrt_akg
from .sub import _sub_akg
