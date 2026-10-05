using System;
using System.Collections.Generic;
using System.Text;

namespace OrderManagement.Domain.Enums
{
    public enum OrderStatus
    {
        Pending = 1,
        Submitted = 2,
        Processing = 3,
        Completed = 4,
        Cancelled = 5,
        Failed = 6
    }
}
