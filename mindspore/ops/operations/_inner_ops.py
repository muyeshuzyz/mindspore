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

"""Inner operators."""

from ..._checkparam import Rel
from ..._checkparam import Validator as validator
from ...common import dtype as mstype
from ..._c_expression import signature_rw as sig_rw
from ..._c_expression import signature_kind as sig_kind
from ..._c_expression import signature_dtype as sig_dtype
from ..primitive import PrimitiveWithInfer, prim_attr_register


class ExtractImagePatches(PrimitiveWithInfer):
    """
    Extract patches from images.
    The input tensor must be a 4-D tensor and the data format is NHWC.

    Args:
        ksizes (Union[tuple[int], list[int]]): The size of sliding window, should be a tuple or list of int,
            and the format is [1, ksize_row, ksize_col, 1].
        strides (Union[tuple[int], list[int]]): Distance between the centers of the two consecutive patches,
            should be a tuple or list of int, and the format is [1, stride_row, stride_col, 1].
        rates (Union[tuple[int], list[int]]): In each extracted patch, the gap between the corresponding dim
            pixel positions, should be a tuple or list of int, and the format is [1, rate_row, rate_col, 1].
        padding (str): The type of padding algorithm, is a string whose value is "same" or "valid",
            not case sensitive. Default: "valid".

            - same: Means that the patch can take the part beyond the original image, and this part is filled with 0.

            - valid: Means that the patch area taken must be completely contained in the original image.

    Inputs:
        - **input_x** (Tensor) - A 4-D tensor whose shape is [in_batch, in_row, in_col, in_depth] and
          data type is number.

    Outputs:
        Tensor, a 4-D tensor whose data type is same as 'input_x',
        and the shape is [out_batch, out_row, out_col, out_depth], the out_batch is same as the in_batch.
    """

    @prim_attr_register
    def __init__(self, ksizes, strides, rates, padding="valid"):
        """init"""
        def _check_tuple_or_list(arg_name, arg_val, prim_name):
            validator.check_value_type(f"{arg_name}s", ksizes, [tuple, list], self.name)
            if len(arg_val) != 4 or arg_val[0] != 1 or arg_val[3] != 1:
                raise ValueError(f"For \'{prim_name}\' the format of {arg_name}s should be [1, {arg_name}_row, "
                                 f"{arg_name}_col, 1], but got {arg_val}.")
            if not isinstance(arg_val[1], int) or not isinstance(arg_val[2], int) or arg_val[1] < 1 or arg_val[2] < 1:
                raise ValueError(f"For '{prim_name}' the {arg_name}_row and {arg_name}_col in {arg_name}s should be an "
                                 f"positive integer number, but got {arg_name}_row is {arg_val[1]}, {arg_name}_col "
                                 f"is {arg_val[2]}")

        _check_tuple_or_list("ksize", ksizes, self.name)
        _check_tuple_or_list("stride", strides, self.name)
        _check_tuple_or_list("rate", rates, self.name)
        self.padding = validator.check_string('padding', padding.upper(), ['VALID', 'SAME'], self.name)
        self.add_prim_attr("padding", self.padding)

    def infer_shape(self, input_x):
        """infer shape"""
        in_batch, in_row, in_col, in_depth = input_x
        _, ksize_row, ksize_col, _ = self.ksizes
        _, stride_row, stride_col, _ = self.strides
        _, rate_row, rate_col, _ = self.rates
        if len(input_x) != 4:
            raise ValueError("The `input_x` should be a 4-D tensor, "
                             f"but got a {len(input_x)}-D tensor whose shape is {input_x}")

        out_batch = in_batch
        out_depth = ksize_row * ksize_col * in_depth

        if self.padding == "VALID":
            out_row = \
                (in_row - (ksize_row + (ksize_row - 1) * (rate_row - 1))) // stride_row + 1
            out_col = \
                (in_col - (ksize_col + (ksize_col - 1) * (rate_col - 1))) // stride_col + 1
        else:
            out_row = (in_row - 1) // stride_row + 1
            out_col = (in_col - 1) // stride_col + 1

        out_shape = [out_batch, out_row, out_col, out_depth]
        return out_shape

    def infer_dtype(self, input_x):
        """infer dtype"""
        validator.check_tensor_type_same({"input_x": input_x}, mstype.number_type, self.name)
        return input_x


class Range(PrimitiveWithInfer):
    r"""
    Creates a sequence of numbers.
    Set `input_x` as :math:`x_i` for each element, `output` as follows:

    .. math::
        \text{output}(x_i) = x_i * \text{delta} + \text{start}

    Args:
        start (float): If `limit` is `None`, the value acts as limit in the range and first entry
            defaults to `0`. Otherwise, it acts as first entry in the range.
        limit (float): Acts as upper limit of sequence. If `None`, defaults to the value of `start`
            while set the first entry of the range to `0`. It can not be equal to `start`.
        delta (float): Increment of the range. It can not be equal to zero. Default: 1.0.

    Inputs:
        - **input_x** (Tensor) - The assistant data. A `1-D` tensor of type float32 or int32.

    Outputs:
        Tensor, has the same shape and dtype as `input_x`.

    Examples:
        >>> range = P.Range(1.0, 8.0, 2.0)
        >>> x = Tensor(np.array([1, 2, 3, 2]), mindspore.int32)
        >>> range(x)
        [3, 5, 7, 5]
    """

    @prim_attr_register
    def __init__(self, start, limit=None, delta=1.0):
        self.init_prim_io_names(inputs=['x'], outputs=['y'])
        self.delta = validator.check_value_type("delta", delta, [float], self.name)
        validator.check_value_type("start", start, [float], self.name)
        if limit is None:
            self.start = 0.0
            self.limit = start
            self.add_prim_attr("start", self.start)
            self.add_prim_attr("limit", self.limit)
        else:
            validator.check_value_type("limit", limit, [float], self.name)
        validator.check('start', self.start, 'limit', self.limit, Rel.NE, self.name)
        if self.delta == 0.0:
            raise ValueError("The input of `delta` can not be equal to zero.")
        if self.delta > 0.0 and self.start > self.limit:
            raise ValueError(f"Limit should be greater than start when delta:{self.delta} is more than zero, "
                             f"but got start:{self.start}, limit:{self.limit}")
        if self.delta < 0.0 and self.start < self.limit:
            raise ValueError(f"Start should be greater than limit when delta:{self.delta} is less than zero, "
                             f"but got start:{self.start}, limit:{self.limit}")

    def infer_shape(self, x_shape):
        return x_shape

    def infer_dtype(self, x_dtype):
        validator.check_tensor_type_same({'x_dtype': x_dtype}, [mstype.float32, mstype.int32], self.name)
        return x_dtype


class Quant(PrimitiveWithInfer):
    r"""
    Returns the quantized value of input_x.

    If `sqrt_mode` is False:

    .. math::
        y = round(scale * x + offset)

    If `sqrt_mode` is True:

    .. math::
        y = round(scale * x * scale + offset)

    Note:
        This operation only support Ascend 310 inference environment.

    Args:
        scale (float) : Specifies the scaling ratio.
        offset (float): Specifies the offset.
        sqrt_mode (bool) : Specifies whether to perform square root on `scale`. Default: False.
        round_mode (str): Specifies the way to round. Should be one of ["Round", "Floor", "Ceil", "Trunc"].
          Default: "Round".

    Inputs:
        - **input_x** (Tensor) : Input tensor. Its data type should be mindspore.float16 or mindspore.float32.

    Outputs:
        - Tensor: The quantized output tensor of type mindspore.int8.

    Examples:
        >>> input_x = Tensor([100.0, 150.0], mstype.float32)
        >>> quant = P.Quant(80.0, 0.0, False, "Round")
        >>> y = quant(input_x)
    """

    @prim_attr_register
    def __init__(self, scale, offset, sqrt_mode=False, round_mode="Round"):
        self.scale = validator.check_value_type("scale", scale, [float], self.name)
        self.offset = validator.check_value_type("offset", offset, [float], self.name)
        self.sqrt_mode = validator.check_value_type("sqrt_mode", sqrt_mode, [bool], self.name)
        self.round_mode = validator.check_string("round_mode", round_mode,
                                                 ["Round", "Floor", "Ceil", "Trunc"], self.name)

    def infer_shape(self, x_shape):
        return x_shape

    def infer_dtype(self, x_type):
        validator.check_subclass("input_x", x_type, mstype.tensor, self.name)
        validator.check_type_name("input_x", x_type, [mstype.float16, mstype.float32], self.name)
        return mstype.int8


class Dequant(PrimitiveWithInfer):
    r"""
    Returns the dequantized value of input_x.
    This operation will do ReLU to the dequantized value if `relu_flag` is True.

    If `sqrt_mode` is False:

    .. math::
        y = x * deq\_scale

    If `sqrt_mode` is True:

    .. math::
        y = x * deq\_scale * deq\_scale

    Note:
        This operation only support Ascend 310 inference environment.

    Args:
        sqrt_mode (bool) : Specifies whether to perform square root on `scale`. Default: False.
        relu_flag (bool): Specifies whether to perform ReLU. Default: False.

    Inputs:
        - **input_x** (Tensor) : Input tensor. Should be mindspore.int32.
        - **deq_scale** (Tensor) : Specifies the scaling ratio.
          Data type should be mindspore.float16 or mindspore.uint64

    Outputs:
        - Tensor: The quantized output tensor of type mindspore.float16.

    Examples:
        >>> input_x = Tensor([100.0, 150.0], mstype.float32)
        >>> dequant = P.Dequant(False, False)
        >>> y = dequant(input_x)
    """
    @prim_attr_register
    def __init__(self, sqrt_mode=False, relu_flag=False):
        self.sqrt_mode = validator.check_value_type("sqrt_mode", sqrt_mode, [bool], self.name)
        self.relu_flag = validator.check_value_type("relu_flag", relu_flag, [bool], self.name)

    def infer_shape(self, x_shape, deq_scale_shape):
        return x_shape

    def infer_dtype(self, x_type, deq_scale_type):
        validator.check_subclass("x", x_type, mstype.tensor, self.name)
        validator.check_type_name("x", x_type, [mstype.int32], self.name)
        validator.check_type_name("deq_scale", deq_scale_type, [mstype.float16, mstype.uint64], self.name)
        return mstype.float16


class SparseApplyFtrlNoReturn(PrimitiveWithInfer):
    """
    Update relevant entries according to the FTRL-proximal scheme.

    Args:
        lr (float): The learning rate value, must be positive.
        l1 (float): l1 regularization strength, must be greater than or equal to zero.
        l2 (float): l2 regularization strength, must be greater than or equal to zero.
        lr_power (float): Learning rate power controls how the learning rate decreases during training,
            must be less than or equal to zero. Use fixed learning rate if `lr_power` is zero.
        use_locking (bool): Use locks for update operation if True . Default: False.

    Inputs:
        - **var** (Parameter): The variable to be updated. The data type must be float32.
        - **accum** (Parameter): The accum to be updated, must be same type and shape as `var`.
        - **linear** (Parameter): The linear to be updated, must be same type and shape as `var`.
        - **grad** (Tensor): A tensor of the same type as `var`, for the gradient.
        - **indices** (Tensor): A vector of indices into the first dimension of `var` and `accum`. The shape
          of `indices` must be the same as `grad` in first dimension. The type must be int32.

    Outputs:
        Tuple of 3 Tensor, this operator will update the input parameters directly, the outputs are useless.

        - **var** (Tensor) - A Tensor with shape (1,).
        - **accum** (Tensor) - A Tensor with shape (1,).
        - **linear** (Tensor) - A Tensor with shape (1,).

    Examples:
        >>> import mindspore
        >>> import mindspore.nn as nn
        >>> import numpy as np
        >>> from mindspore import Parameter
        >>> from mindspore import Tensor
        >>> from mindspore.ops import operations as P
        >>> class SparseApplyFtrlNet(nn.Cell):
        >>>     def __init__(self):
        >>>         super(SparseApplyFtrlNet, self).__init__()
        >>>         self.sparse_apply_ftrl = P.SparseApplyFtrlV2(lr=0.01, l1=0.0, l2=0.0, lr_power=-0.5)
        >>>         self.var = Parameter(Tensor(np.random.rand(3, 1, 2).astype(np.float32)), name="var")
        >>>         self.accum = Parameter(Tensor(np.random.rand(3, 1, 2).astype(np.float32)), name="accum")
        >>>         self.linear = Parameter(Tensor(np.random.rand(3, 1, 2).astype(np.float32)), name="linear")
        >>>
        >>>     def construct(self, grad, indices):
        >>>         out = self.sparse_apply_ftrl(self.var, self.accum, self.linear, grad, indices)
        >>>         return out
        >>>
        >>> net = SparseApplyFtrlNet()
        >>> grad = Tensor(np.random.rand(2, 1, 2).astype(np.float32))
        >>> indices = Tensor(np.array([0, 1]).astype(np.int32))
        >>> output = net(grad, indices)
    """
    __mindspore_signature__ = (
        ('var', sig_rw.RW_WRITE, sig_kind.KIND_POSITIONAL_KEYWORD, sig_kind.KIND_EMPTY_DEFAULT_VALUE, sig_dtype.T),
        ('accum', sig_rw.RW_WRITE, sig_kind.KIND_POSITIONAL_KEYWORD, sig_kind.KIND_EMPTY_DEFAULT_VALUE, sig_dtype.T),
        ('linear', sig_rw.RW_WRITE, sig_kind.KIND_POSITIONAL_KEYWORD, sig_kind.KIND_EMPTY_DEFAULT_VALUE, sig_dtype.T),
        ('grad', sig_rw.RW_READ, sig_kind.KIND_POSITIONAL_KEYWORD, sig_kind.KIND_EMPTY_DEFAULT_VALUE, sig_dtype.T),
        ('indices', sig_rw.RW_READ, sig_kind.KIND_POSITIONAL_KEYWORD, sig_kind.KIND_EMPTY_DEFAULT_VALUE, sig_dtype.T1)
    )

    @prim_attr_register
    def __init__(self, lr, l1, l2, lr_power, use_locking=False):
        self.init_prim_io_names(inputs=['var', 'accum', 'linear', 'grad', 'indices'],
                                outputs=['output'])
        validator.check_value_type("lr", lr, [float], self.name)
        validator.check_value_type("l1", l1, [float], self.name)
        validator.check_value_type("l2", l2, [float], self.name)
        validator.check_value_type("lr_power", lr_power, [float], self.name)
        self.lr = validator.check_number_range("lr", lr, 0.0, float("inf"), Rel.INC_NEITHER, self.name)
        self.l1 = validator.check_number_range("l1", l1, 0.0, float("inf"), Rel.INC_LEFT, self.name)
        self.l2 = validator.check_number_range("l2", l2, 0.0, float("inf"), Rel.INC_LEFT, self.name)
        self.lr_power = validator.check_number("lr_power", lr_power, 0, Rel.LE, self.name)
        self.use_locking = validator.check_value_type("use_locking", use_locking, [bool], self.name)
        self.add_prim_attr('primitive_target', 'CPU')

    def infer_shape(self, var_shape, accum_shape, linear_shape, grad_shape, indices_shape):
        validator.check('var shape', var_shape, 'accum shape', accum_shape, Rel.EQ, self.name)
        validator.check('var shape', var_shape, 'linear shape', linear_shape, Rel.EQ, self.name)
        if len(var_shape) > 1:
            validator.check('var_shape[1:]', var_shape[1:], 'grad_shape[1:]', grad_shape[1:], Rel.EQ, self.name)
        validator.check_integer("indices rank", len(indices_shape), 1, Rel.EQ, self.name)
        validator.check('grad_shape[0]', grad_shape[0], 'indices_shape[0]', indices_shape[0], Rel.EQ, self.name)
        return [1], [1], [1]

    def infer_dtype(self, var_dtype, accum_dtype, linear_dtype, grad_dtype, indices_dtype):
        args = {"var_dtype": var_dtype, "accum_dtype": accum_dtype,
                "linear_dtype": linear_dtype, "grad_dtype": grad_dtype}
        validator.check_tensor_type_same(args, [mstype.float32], self.name)
        validator.check_tensor_type_same({"indices_dtype": indices_dtype}, [mstype.int32], self.name)
        return var_dtype, accum_dtype, linear_dtype


class SparseApplyProximalAdagradNoReturn(PrimitiveWithInfer):
    r"""
    Updates relevant entries according to the proximal adagrad algorithm.

    .. math::
            accum += grad * grad
    .. math::
            \text{prox_v} = var - lr * grad * \frac{1}{\sqrt{accum}}
    .. math::
            var = \frac{sign(\text{prox_v})}{1 + lr * l2} * \max(\left| \text{prox_v} \right| - lr * l1, 0)

    Args:
        use_locking (bool): If True, updating of the var and accum tensors will be protected. Default: False.

    Inputs:
        - **var** (Parameter) - Variable tensor to be updated. The data type must be float32.
        - **accum** (Parameter) - Variable tensor to be updated. Has the same dtype as `var`.
        - **lr** (Tensor): The learning rate value. The data type must be float32.
        - **l1** (Tensor): l1 regularization strength. The data type must be float32.
        - **l2** (Tensor): l2 regularization strength. The data type must be float32.
        - **grad** (Tensor) - A tensor of the same type as `var`, for the gradient. The data type must be float32.
        - **indices** (Tensor) - A vector of indices into the first dimension of `var` and `accum`. The data type
          must be int32.

    Outputs:
        Tuple of 2 Tensor, this operator will update the input parameters directly, the outputs are useless.

        - **var** (Tensor) - A Tensor with shape (1,).
        - **accum** (Tensor) - A Tensor with shape (1,).

    Examples:
        >>> import numpy as np
        >>> import mindspore.nn as nn
        >>> from mindspore import Tensor, Parameter
        >>> from mindspore.ops import operations as P
        >>> class Net(nn.Cell):
        >>>     def __init__(self):
        >>>         super(Net, self).__init__()
        >>>         self.sparse_apply_proximal_adagrad = P.SparseApplyProximalAdagradV2()
        >>>         self.var = Parameter(Tensor(np.random.rand(3, 1, 2).astype(np.float32)), name="var")
        >>>         self.accum = Parameter(Tensor(np.random.rand(3, 1, 2).astype(np.float32)), name="accum")
        >>>         self.lr = Tensor(0.01, mstype.float32)
        >>>         self.l1 = Tensor(0.0, mstype.float32)
        >>>         self.l2 = Tensor(0.0, mstype.float32)
        >>>     def construct(self, grad, indices):
        >>>         out = self.sparse_apply_proximal_adagrad(self.var, self.accum, self.lr, self.l1,
        >>>                                                  self.l2, grad, indices)
        >>>         return out
        >>> net = Net()
        >>> grad = Tensor(np.random.rand(2, 1, 2).astype(np.float32))
        >>> indices = Tensor(np.array([0, 1]).astype(np.int32))
        >>> output = net(grad, indices)
    """
    __mindspore_signature__ = (
        ('var', sig_rw.RW_WRITE, sig_kind.KIND_POSITIONAL_KEYWORD, sig_kind.KIND_EMPTY_DEFAULT_VALUE, sig_dtype.T),
        ('accum', sig_rw.RW_WRITE, sig_kind.KIND_POSITIONAL_KEYWORD, sig_kind.KIND_EMPTY_DEFAULT_VALUE, sig_dtype.T),
        ('lr', sig_rw.RW_READ, sig_kind.KIND_POSITIONAL_KEYWORD, sig_kind.KIND_EMPTY_DEFAULT_VALUE, sig_dtype.T),
        ('l1', sig_rw.RW_READ, sig_kind.KIND_POSITIONAL_KEYWORD, sig_kind.KIND_EMPTY_DEFAULT_VALUE, sig_dtype.T),
        ('l2', sig_rw.RW_READ, sig_kind.KIND_POSITIONAL_KEYWORD, sig_kind.KIND_EMPTY_DEFAULT_VALUE, sig_dtype.T),
        ('grad', sig_rw.RW_READ, sig_kind.KIND_POSITIONAL_KEYWORD, sig_kind.KIND_EMPTY_DEFAULT_VALUE, sig_dtype.T),
        ('indices', sig_rw.RW_READ, sig_kind.KIND_POSITIONAL_KEYWORD, sig_kind.KIND_EMPTY_DEFAULT_VALUE, sig_dtype.T1)
    )

    @prim_attr_register
    def __init__(self, use_locking=False):
        self.init_prim_io_names(inputs=['var', 'accum', 'lr', 'l1', 'l2', 'grad', 'indices'],
                                outputs=['output'])
        self.use_locking = validator.check_value_type("use_locking", use_locking, [bool], self.name)
        self.add_prim_attr('primitive_target', 'CPU')

    def infer_shape(self, var_shape, accum_shape, lr_shape, l1_shape, l2_shape, grad_shape, indices_shape):
        validator.check_integer("indices rank", len(indices_shape), 1, Rel.EQ, self.name)
        return [1], [1]

    def infer_dtype(self, var_dtype, accum_dtype, lr_dtype, l1_dtype, l2_dtype, grad_dtype, indices_dtype):
        args = {'var': var_dtype, 'accum': accum_dtype, 'grad': grad_dtype}
        validator.check_tensor_type_same(args, [mstype.float32], self.name)
        validator.check_scalar_or_tensor_type_same({"lr": lr_dtype}, [mstype.float32], self.name)
        validator.check_scalar_or_tensor_type_same({"l1": l1_dtype}, [mstype.float32], self.name)
        validator.check_scalar_or_tensor_type_same({"l2": l2_dtype}, [mstype.float32], self.name)
        valid_types = [mstype.int16, mstype.int32, mstype.int64,
                       mstype.uint16, mstype.uint32, mstype.uint64]
        validator.check_tensor_type_same({'indices': indices_dtype}, valid_types, self.name)
        return var_dtype, accum_dtype


class LinSpace(PrimitiveWithInfer):
    r"""
    Generates values in an interval. And return the corresponding interpolation accroding to assist.

    Inputs:
        - **assist** (Tensor[float32]) - The assist value, With shape of 0-D or 1-D.
        - **start** (Tensor[float32]) - The start of interval, With shape of 0-D.
        - **stop** (Tensor[float32]) - The end of interval, With shape of 0-D.
        - **num** (Tensor[int32]) - ticks number in the interval, the ticks include start and stop value.
          With shape of 0-D.

    Outputs:
        Tensor, has the same shape as `assist`.

    Examples:
        >>> linspace = P.LinSpace()
        >>> assist = Tensor([5, 5.5], mindspore.float32)
        >>> start = Tensor(1, mindspore.float32)
        >>> stop = Tensor(10, mindspore.float32)
        >>> num = Tensor(5, mindspore.int32)
        >>> output = linspace(assist, start, stop, num)
        [12.25, 13.375]
    """

    @prim_attr_register
    def __init__(self):
        pass

    def infer_shape(self, assist, start, stop, num):
        return assist

    def infer_dtype(self, assist, start, stop, num):
        args = {"num": num}
        validator.check_tensor_type_same(args, (mstype.int32,), self.name)
        args = {"assist": assist, "start": start, "stop": stop}
        validator.check_tensor_type_same(args, (mstype.float32,), self.name)
        return assist


class MatrixDiag(PrimitiveWithInfer):
    """
    Returns a batched diagonal tensor with a given batched diagonal values.

    Inputs:
        - **x** (Tensor) - A tensor which to be element-wise multi by `assist`. It can be of the following data types:
          float32, float16, int32, int8, uint8.
        - **assist** (Tensor) - A eye tensor of the same type as `x`. It's rank must greater than or equal to 2 and
          it's last dimension must equal to the second to last dimension.

    Outputs:
        Tensor, has the same type and shape as input `assist`.

    Examples:
        >>> x = Tensor(np.array([1, -1]), mstype.float32)
        >>> assist = Tensor(np.arange(-12, 0).reshape(3, 2, 2), mindspore.float32)
        >>> matrix_diag = P.MatrixDiag()
        >>> result = matrix_diag(x, assist)
        [[[-12.   11.]
          [-10.    9.]]
         [[ -8.    7.]
          [ -6.    5.]]
         [[ -4.    3.]
          [ -2.    1.]]]
    """

    @prim_attr_register
    def __init__(self):
        """init MatrixDiag"""

    def infer_dtype(self, x_dtype, assist_dtype):
        valid_type = [mstype.float16, mstype.float32, mstype.int32, mstype.int8, mstype.uint8]
        args = {"x": x_dtype, "assist": assist_dtype}
        validator.check_tensor_type_same(args, valid_type, self.name)
        return x_dtype

    def infer_shape(self, x_shape, assist_shape):
        validator.check_integer("assist rank", len(assist_shape), 2, Rel.GE, self.name)
        validator.check('rank of x', len(x_shape)+1,
                        'rank of assist', len(assist_shape), Rel.LE, self.name)
        validator.check('assist\'s penultimate dimension', assist_shape[-2], 'assist\'s last dimension',
                        assist_shape[-1], Rel.EQ, self.name)

        r_end_dim = -len(x_shape)
        r_idx = -1
        while r_idx >= r_end_dim:
            if x_shape[r_idx] != 1:
                validator.check("reverse x dim %d" % r_idx, x_shape[r_idx], "reverse assist dim %d" %
                                assist_shape[r_idx-1], assist_shape[r_idx-1], Rel.EQ, self.name)
            r_idx = r_idx - 1

        return assist_shape


class MatrixDiagPart(PrimitiveWithInfer):
    r"""
    Returns the batched diagonal part of a batched tensor.

    Inputs:
        - **x** (Tensor) - The batched tensor. It can be of the following data types:
          float32, float16, int32, int8, uint8.
        - **assist** (Tensor) - A eye tensor of the same type as `x`. With shape same as `x`.

    Outputs:
        Tensor, data type same as input `x`. The shape should be x.shape[:-2] + [min(x.shape[-2:])].

    Examples:
        >>> x = Tensor([[[-1, 0], [0, 1]], [[-1, 0], [0, 1]], [[-1, 0], [0, 1]]], mindspore.float32)
        >>> assist = Tensor(np.arange(-12, 0).reshape(3, 2, 2), mindspore.float32)
        >>> matrix_diag_part = P.MatrixDiagPart()
        >>> result = matrix_diag_part(x, assist)
        [[12., -9.], [8., -5.], [4., -1.]]
    """

    @prim_attr_register
    def __init__(self):
        """init MatrixDiagPart"""

    def infer_dtype(self, x_dtype, assist_dtype):
        valid_type = [mstype.float16, mstype.float32, mstype.int32, mstype.int8, mstype.uint8]
        args = {"x": x_dtype, "assist": assist_dtype}
        validator.check_tensor_type_same(args, valid_type, self.name)
        return x_dtype

    def infer_shape(self, x_shape, assist_shape):
        validator.check_integer("x rank", len(x_shape), 2, Rel.GE, self.name)
        validator.check("x shape", x_shape, "assist shape", assist_shape, Rel.EQ, self.name)

        if assist_shape[-2] < assist_shape[-1]:
            out_shape = assist_shape[:-1]
        else:
            out_shape = assist_shape[:-2] + assist_shape[-1:]
        return out_shape


class MatrixSetDiag(PrimitiveWithInfer):
    r"""
    Modify the batched diagonal part of a batched tensor.

    Inputs:
        - **x** (Tensor) - The batched tensor. It can be of the following data types:
          float32, float16, int32, int8, uint8.
        - **assist** (Tensor) - A eye tensor of the same type as `x`. With shape same as `x`.
        - **diagonal** (Tensor) - The diagonal values.

    Outputs:
        Tensor, data type same as input `x`. The shape same as `x`.

    Examples:
        >>> x = Tensor([[[-1, 0], [0, 1]], [[-1, 0], [0, 1]], [[-1, 0], [0, 1]]], mindspore.float32)
        >>> diagonal = Tensor([[-1., 2.], [-1., 1.], [-1., 1.]], mindspore.float32)
        >>> matrix_set_diag = P.MatrixSetDiag()
        >>> result = matrix_set_diag(x, diagonal)
        [[[-1, 0], [0, 2]], [[-1, 0], [0, 1]], [[-1, 0], [0, 1]]]

    """

    @prim_attr_register
    def __init__(self):
        """init MatrixSetDiag"""

    def infer_dtype(self, x_dtype, diagonal_dtype, assist_dtype):
        valid_type = [mstype.float16, mstype.float32, mstype.int32, mstype.int8, mstype.uint8]
        args = {"x": x_dtype, "diagonal": diagonal_dtype, "assist": assist_dtype}
        validator.check_tensor_type_same(args, valid_type, self.name)
        return x_dtype

    def infer_shape(self, x_shape, diagonal_shape, assist_shape):
        validator.check_integer("x rank", len(x_shape), 2, Rel.GE, self.name)
        validator.check("x shape", x_shape, "assist shape", assist_shape, Rel.EQ, self.name)

        if x_shape[-2] < x_shape[-1]:
            validator.check("diagnoal shape", diagonal_shape, "x shape excluding the last dimension",
                            x_shape[:-1], Rel.EQ, self.name)
        else:
            validator.check("diagonal shape", diagonal_shape, "x shape excluding the second last dimension",
                            x_shape[:-2] + x_shape[-1:], Rel.EQ, self.name)

        return assist_shape
