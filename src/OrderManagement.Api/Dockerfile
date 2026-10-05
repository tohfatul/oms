# ----------------------------
# Build stage
# ----------------------------
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build

WORKDIR /src

# Copy project files first for better Docker layer caching
COPY ["src/OrderManagement.Api/OrderManagement.Api.csproj", "src/OrderManagement.Api/"]
COPY ["src/OrderManagement.Application/OrderManagement.Application.csproj", "src/OrderManagement.Application/"]
COPY ["src/OrderManagement.Domain/OrderManagement.Domain.csproj", "src/OrderManagement.Domain/"]
COPY ["src/OrderManagement.Infrastructure/OrderManagement.Infrastructure.csproj", "src/OrderManagement.Infrastructure/"]

RUN dotnet restore "src/OrderManagement.Api/OrderManagement.Api.csproj"

# Copy remaining source code
COPY . .

RUN dotnet publish \
    "src/OrderManagement.Api/OrderManagement.Api.csproj" \
    -c Release \
    -o /app/publish \
    --no-restore

# ----------------------------
# Runtime stage
# ----------------------------

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgssapi-krb5-2 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/publish .

ENV ASPNETCORE_URLS=http://+:8080
ENV ASPNETCORE_ENVIRONMENT=Production

EXPOSE 8080

ENTRYPOINT ["dotnet", "OrderManagement.Api.dll"]