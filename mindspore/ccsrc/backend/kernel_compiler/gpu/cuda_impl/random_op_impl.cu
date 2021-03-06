/**
 * Copyright 2020 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */ 

#include "random_op_impl.cuh"
template <typename T>
__global__ void NormalKernel(int seed, curandState *globalState, T *output, size_t count) {
  for (size_t i = blockIdx.x * blockDim.x + threadIdx.x; i < (count); i += blockDim.x * gridDim.x) {
    curand_init(seed, i, 0, &globalState[i]);
    output[i] = curand_normal(&globalState[i]);
  }
  return;
}

template <typename T>
void StandardNormal(int seed, int seed2, curandState *globalState, T *output, size_t count, cudaStream_t cuda_stream) {
  int RNG_seed = 0;
  if (seed2 != 0) {
    RNG_seed = seed2;
  } else if (seed != 0) {
    RNG_seed = seed;
  } else {
    RNG_seed = time(NULL);
  }
  NormalKernel<<<GET_BLOCKS(count), GET_THREADS, 0, cuda_stream>>>(RNG_seed, globalState, output, count);
  return;
}

template void StandardNormal<float>(int seed, int seed2, curandState *globalState,
                                    float *output, size_t count, cudaStream_t cuda_stream);
