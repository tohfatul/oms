using System;
using System.Collections.Generic;
using System.Text;

namespace OrderManagement.Application.Common;

public class ValidationException : Exception
{
    public ValidationException(string message) : base(message)
    {
    }
}
