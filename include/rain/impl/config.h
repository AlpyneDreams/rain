#pragma once

#include <cstdint>

#if !defined(RAIN_HASH_TYPE)
    #define RAIN_HASH_TYPE std::uint32_t
#endif

#if defined(__clang__) || defined(__GNUC__)
#    define RAIN_FUNCTION_NAME __PRETTY_FUNCTION__
#    define RAIN_FUNCTION_NAME_PREFIX '='
#    define RAIN_FUNCTION_NAME_SUFFIX ']'
#elif defined(_MSC_VER)
#    define RAIN_FUNCTION_NAME __FUNCSIG__
#    define RAIN_FUNCTION_NAME_PREFIX '<'
#    define RAIN_FUNCTION_NAME_SUFFIX '>'
#endif

namespace rain
{
    using Hash = RAIN_HASH_TYPE;

    // Must be large enough to contain any enum value.
    using uintmax = std::uintmax_t;

    namespace internal
    {
        using uint64 = std::uint64_t;
        using uint32 = std::uint32_t;
    }
}