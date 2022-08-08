#pragma once

#include <string_view>
#include <type_traits>

#include "config.h"

namespace rain::internal
{
// Type Traits //
    template <typename T>
    using PlainType = std::remove_cv_t<std::remove_reference_t<T>>;

// Type Name //

    template<typename T>
    [[nodiscard]] constexpr auto GetTypeName() noexcept {
    #if defined(RAIN_FUNCTION_NAME)
        std::string_view name {RAIN_FUNCTION_NAME};
        // Strip prefix, suffix, and leading whitespace
        auto prefix = name.find_first_of(RAIN_FUNCTION_NAME_PREFIX);
        auto suffix = name.find_last_of(RAIN_FUNCTION_NAME_SUFFIX);
        auto first  = name.find_first_not_of(' ', prefix + 1);
        auto value  = name.substr(first, suffix - first);
        return value;
    #else
        return std::string_view("");
    #endif
    }

// Type Hash //

    // Standard FNV 1a String Hash Function
    // Using Hash = uint32 provides compatibility with EnTT.

    template <typename T> struct FNV_1a;
    
    template <> struct FNV_1a<uint32> {
        static constexpr uint32 offset = 2166136261u;
        static constexpr uint32 prime  = 16777619u;
    };

    template <> struct FNV_1a<uint64> {
        static constexpr std::uint64_t offset = 14695981039346656037ull;
        static constexpr std::uint64_t prime  = 1099511628211ull;
    };

    constexpr Hash HashString(const char* str, size_t count) {
        return !count
            ? FNV_1a<Hash>::offset
            : (HashString(str, count - 1) ^ str[count-1]) * FNV_1a<Hash>::prime;
    }

    template <typename T>
    constexpr Hash GetTypeHash() noexcept {
        constexpr auto name = GetTypeName<T>();
        constexpr auto value = HashString(name.data(), name.size());
        return value;
    }


// Type Index //

    [[nodiscard]] inline Hash NextTypeIndex() noexcept {
        static Hash value;
        return value++;
    }

    template <typename T>
    [[nodiscard]] inline Hash GetTypeIndex() noexcept {
        static const Hash index = NextTypeIndex();
        return index;
    }

}
