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

#ifndef MINDSPORE_MINDSPORE_CCSRC_DEVICE_ASCEND_DUMP_DATADUMP_H_
#define MINDSPORE_MINDSPORE_CCSRC_DEVICE_ASCEND_DUMP_DATADUMP_H_
#include <tuple>
#include <map>
#include <memory>
#include <string>
#include <vector>
#include "backend/session/kernel_graph.h"

namespace aicpu {
namespace dump {
class OpMappingInfo;
class Task;
}  // namespace dump
}  // namespace aicpu
namespace mindspore {
namespace device {
namespace ascend {
// tuple(op_name, task_id, stream_id, args)
using RuntimeInfo = std::tuple<uint32_t, uint32_t, void *>;
class DataDumper {
 public:
  DataDumper(const session::KernelGraph *kernel_graph,
             const std::map<std::string, std::shared_ptr<RuntimeInfo>> &runtime_info_map)
      : load_flag_(false),
        dev_load_mem_(nullptr),
        dev_unload_mem_(nullptr),
        graph_id_(UINT32_MAX),
        kernel_graph_(kernel_graph),
        runtime_info_map_(runtime_info_map) {}
  ~DataDumper();
  void LoadDumpInfo();

  void UnloadDumpInfo();

 private:
  void ReleaseDevMem(void **ptr) const;
  bool KernelNeedDump(const CNodePtr &kernel) const;
  void SetOpMappingInfo(NotNull<aicpu::dump::OpMappingInfo *> dump_info) const;
  void ConstructDumpTask(NotNull<const CNodePtr &> kernel, NotNull<aicpu::dump::Task *> dump_task) const;

  bool load_flag_;
  void *dev_load_mem_;
  void *dev_unload_mem_;
  uint32_t graph_id_;
  std::vector<std::string> dump_kernel_names_;
  const session::KernelGraph *kernel_graph_;
  std::map<std::string, std::shared_ptr<RuntimeInfo>> runtime_info_map_;
};
}  // namespace ascend
}  // namespace device
}  // namespace mindspore
#endif  // MINDSPORE_MINDSPORE_CCSRC_DEVICE_ASCEND_DUMP_DATADUMP_H_
