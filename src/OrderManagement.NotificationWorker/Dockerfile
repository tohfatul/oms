# ----------------------------
# Build stage
# ----------------------------
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build

WORKDIR /src

COPY ["src/OrderManagement.NotificationWorker/OrderManagement.NotificationWorker.csproj", "src/OrderManagement.NotificationWorker/"]
COPY ["src/OrderManagement.Application/OrderManagement.Application.csproj", "src/OrderManagement.Application/"]
COPY ["src/OrderManagement.Domain/OrderManagement.Domain.csproj", "src/OrderManagement.Domain/"]

RUN dotnet restore "src/OrderManagement.NotificationWorker/OrderManagement.NotificationWorker.csproj"

COPY . .

RUN dotnet publish \
    "src/OrderManagement.NotificationWorker/OrderManagement.NotificationWorker.csproj" \
    -c Release \
    -o /app/publish \
    --no-restore

# ----------------------------
# Runtime stage
# ----------------------------
FROM mcr.microsoft.com/dotnet/runtime:10.0 AS final

WORKDIR /app

COPY --from=build /app/publish .

ENV DOTNET_ENVIRONMENT=Production

ENTRYPOINT ["dotnet", "OrderManagement.NotificationWorker.dll"]