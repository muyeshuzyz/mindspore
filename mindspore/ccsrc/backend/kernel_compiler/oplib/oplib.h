/**
 * Copyright 2019 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_CCSRC_KERNEL_OPLIB_OPLIB_H_
#define MINDSPORE_CCSRC_KERNEL_OPLIB_OPLIB_H_
#include <vector>
#include <string>
#include <memory>
#include <nlohmann/json.hpp>
#include "backend/kernel_compiler/oplib/opinfo.h"

namespace mindspore {
namespace kernel {
class OpLib {
 public:
  OpLib() = default;
  virtual ~OpLib() = default;
  static bool RegOp(const std::string &json_string, const std::string &impl_path);
  static void RegOpInfo(const std::shared_ptr<OpInfo> &opinfo) { op_info_.emplace_back(opinfo); }
  static std::shared_ptr<OpInfo> FindOp(const std::string &op_name, OpImplyType imply_type);
  static const std::vector<std::shared_ptr<OpInfo>> &GetAllOpsInfo() { return op_info_; }

 protected:
  static std::vector<std::shared_ptr<OpInfo>> op_info_;

 private:
  static bool RegOpFromLocalInfo();
  static bool DecodeOpInfo(const nlohmann::json &obj, const OpImplyType imply_type, const std::string &impl_path);
  static bool DecodeAttr(const nlohmann::json &obj, const OpImplyType imply_type,
                         const std::shared_ptr<OpInfo> &op_info);
  static bool DecodeDtypeFormat(const nlohmann::json &dtype_format, const std::shared_ptr<OpIOInfo> &op_io,
                                size_t index);
  static void DecodeTBESpecificInfo(const nlohmann::json &obj, const std::shared_ptr<OpInfo> &op_info);
  static void DecodeAKGSpecificInfo(const nlohmann::json &obj, const std::shared_ptr<OpInfo> &op_info);
  static bool DecodeInputOutput(const nlohmann::json &obj, const OpImplyType imply_type, const OpIOType io_type,
                                const std::shared_ptr<OpInfo> &op_info, const nlohmann::json &dtype_format);
  static bool GetRefInfo(const std::shared_ptr<OpInfo> &op_info);
  static bool CheckRepetition(const std::shared_ptr<OpInfo> &op_info);
};
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_KERNEL_OPLIB_OPLIB_H_
