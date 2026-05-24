# Многоступенчатая сборка C++ бэкенда
FROM gcc:13 AS builder

WORKDIR /app
COPY . .

# Простая сборка — замените на ваш build-скрипт (cmake / make)
RUN if [ -f CMakeLists.txt ]; then \
        apt-get update && apt-get install -y cmake && \
        cmake -B build && cmake --build build -j && \
        cp build/server /app/server; \
    elif [ -f main.cpp ]; then \
        g++ -O2 -std=c++17 -o server main.cpp -lpthread; \
    else \
        echo '#include <iostream>\nint main(){std::cout<<"backend stub\\n";while(true){sleep(60);}return 0;}' > stub.cpp && \
        g++ -O2 -std=c++17 -o server stub.cpp; \
    fi

FROM debian:bookworm-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
        libstdc++6 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/server .

EXPOSE 8080
CMD ["./server"]
