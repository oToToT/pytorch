#pragma once

#include <ATen/core/ivalue.h>
#include <functional>
#include <vector>

namespace torch {
namespace jit {
namespace mobile {

using Stack = std::vector<c10::IValue>;

void registerPrimOpsFunction(
    const std::string name,
    const std::function<void(Stack&)> fn);

bool hasPrimOpsFn(const std::string& name);

std::function<void(Stack&)>& getPrimOpsFn(const std::string& name);

} // namespace mobile
} // namespace jit
} // namespace torch
