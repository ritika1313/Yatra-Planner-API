Project Statement:
A Goa-Based Startup wants an API that aggregates (collect data from different - different website and collect into one place) then data from multiple external sources (weather, currency, places) into a single travel plan. They need both a standard endpoint and a streaming endpoint so thier mobile app can show data progressively as it loads.

A travel planning API that fetches weather, exchange rates, and place of interest concurrently

For Streaming endpoint we are using Server-Sent Events (SSE) endpoint that streams each section as it become available.

Because we are collecting data from external resource so we need In - memory cache , not using a chache causing a lot of problem (1) Latency increase (because we are dependent on external things like getting the weather data)

In-memory cache with TTL to avoid redundant API calls

Clean service layer with simulated data (swappable with real APIs)

Server Sent Events= Basically ek br client ke through request gye then server ne response bja then yeh request and response cycle khtm hoo gye ab hum na to koi request bje skte h na hi koi resonse but when the header Content-Type: text/event-stream then it is streaming isme hum multiple time response bje skte h in the form of the chunk(small piece of data) but make sure the flow of the data is only in one direction ythrough servre side koi bhi client side se req nhi ja skte tb, after the stream work is complete then we can close the connection. Benefits of this: we can send the data in the form of the chunks instead of sending them complete jitta jitta jse jse load hota rhega data use hum real time bjte rhege, if the data is changing on the backend then we can send the changes

Ex: let's take the example of the stock market APIs there request is goes at realtime-data and in the response there is streaming sometime stock price increae some time decrease buyer will increase seller will incraese so the backend will continously increasig and it will referect the data if this concept did not exist we need to go to the websocket or polling (like after every sec give me the fresh data )

Explanation of Project
My project is Yatra Planner API, a travel data aggregation API developed using FastAPI and Python.

The main objective is to provide travel-related information from multiple sources through a single API. It combines weather forecasts, currency exchange rates, and tourist attractions for a selected destination.

I divided the application into routes, models, and services to keep the code modular and maintainable. The routes handle incoming requests, Pydantic models define the request and response data structures, and the service layer handles data fetching.

For performance, I use asynchronous programming with asyncio.gather() to fetch weather, currency, and places concurrently in the standard endpoint. I also implemented an in-memory cache with a time-to-live mechanism to reduce repeated external API calls.

One important feature is that the application supports both a standard endpoint, which returns the complete travel plan as JSON, and an SSE streaming endpoint, which sends progress and data in separate events as each section becomes available.

I used FastAPI, Pydantic, HTTPX, Python's asyncio module, and Server-Sent Events to implement these features.

Can you explain the architecture?
I followed a modular architecture. The routes are responsible for API-level logic, the service layer isolates data-fetching logic, and Pydantic models define the data structure. This separation makes the code easier to test, maintain and extend.

What is TTL?
Answer: “TTL stands for Time To Live. It defines how long a cached entry is considered valid. My cache records the insertion timestamp and TTL, and when an entry is requested, it checks whether the elapsed time exceeds the TTL.”

What problem does caching solve?
“Without caching, repeated requests for the same weather forecast or currency rates would repeatedly call external services. Caching reduces redundant network requests, usually improves response time for repeated requests and can reduce external API usage.

Why use in-memory caching instead of Redis or a database?
“For this project, an in-memory dictionary keeps the implementation simple and demonstrates the caching concept without requiring another service. For a production application with multiple workers or instances, I would consider Redis because it can provide shared cache storage.

What exactly is SSE?
SSE is a mechanism for sending a continuous stream of events from a server to a client over a single HTTP response. The connection remains open while the server produces events. The server can send multiple updates without requiring a new request for every update. A standard SSE response uses the Content-Type: text/event-stream header.

Important correction to your understanding: SSE is unidirectional for that connection, from server to client. The client can still make other HTTP requests separately. SSE does not prevent the client from sending requests; it just does not carry client-to-server messages over the same event stream.
Why did you use SSE instead of polling or WebSockets?
Feature SSE Polling WebSockets Communication Server → client Repeated request and response Two-way Connection Long-lived HTTP response Repeated HTTP requests Persistent WebSocket connection Updates Server pushes events Client checks repeatedly Either side can send messages Best fit Progress and live feeds Simple periodic checks Interactive real-time applications

Interview answer: “I chose SSE because my requirement is to deliver travel-plan sections progressively from the server to the mobile app. The client mainly needs to receive updates, so full-duplex communication through WebSockets is unnecessary for this use case. Compared with polling, SSE avoids repeatedly requesting updates just to check whether data is ready.
What is the difference between async and await?
“async defines a coroutine function, while await allows that coroutine to suspend while waiting for another awaitable operation. This lets the event loop work on other tasks instead of blocking while waiting for network I/O.”

What is the difference between concurrency and parallelism?
“Concurrency means multiple tasks can make progress during overlapping periods. Parallelism means multiple operations execute at the same time. My use of asyncio.gather() is asynchronous concurrency, particularly suitable for network requests.”

Goal 1 — Identify external operations that can execute independently
Interviewer: Which operations in your travel planning API can execute independently, and how did you identify them?

In my Yatra Planner API, I need to collect three types of information: weather forecasts, currency exchange rates, and places of interest.
These operations are independent because the result of one operation is not required to start another. For example, I don't need the weather forecast before I can fetch currency rates, and I don't need currency rates before retrieving tourist attractions.

So, after validating the user's travel request, I can fetch these three sections concurrently using asyncio.gather().

The weather service calls an external WeatherAPI, the currency service calls an exchange-rate API, and the places service currently retrieves data from a predefined local dataset.

I kept these operations separate in the service layer so that each service has its own responsibility and can be maintained or replaced independently.

However, the input validation must happen first because all three operations depend on the user's request being valid.

This approach avoids unnecessary sequential waiting and helps reduce the overall response time.

Goal 2 — Explain where AsyncIO can improve an I/O-heavy FastAPI workflow
Interviewer: Why did you use asynchronous programming in your project? How does it improve performance?

My project depends on external HTTP APIs, and network requests can take time because the application has to wait for responses from external servers.
I use async def, await, HTTPX's AsyncClient, and asyncio.gather() to handle these I/O-bound operations asynchronously.

In my standard endpoint, I use asyncio.gather() to coordinate the weather, places, and currency operations instead of waiting for each operation to finish sequentially.

For example, if fetching weather takes three seconds, currency takes two seconds, and places takes one second, sequential execution could take around six seconds. If the operations overlap fully, concurrent execution could take approximately three seconds, depending on network latency and overhead.

While an asynchronous task is waiting for network I/O, the event loop can make progress on other tasks instead of blocking the thread for that wait.

This makes asynchronous programming particularly useful for an API that aggregates information from multiple independent sources.

However, asynchronous programming does not automatically make CPU-intensive operations faster, and it does not guarantee that every request will be faster. The actual improvement depends on the workload, caching and external API response times.

Goal 3 — Explain when Server-Sent Events and StreamingResponse are appropriate
Interviewer: Why did you implement SSE in your project, and when would you use it instead of a normal API response?

I implemented SSE because I wanted the client application to receive travel-plan information progressively instead of waiting for the complete result.
In a normal endpoint, my application fetches all the required sections and returns them together in one JSON response. In the streaming endpoint, I use an asynchronous generator that produces events as the workflow progresses.

For example, I first send a start event, then a weather-fetching status, followed by the weather result. I then send the places result, the currency result, and finally a completion event.

I use yield to produce events, StreamingResponse to send the generator's output progressively, and the text/event-stream media type to identify the SSE response.

Each event contains an optional event name and a JSON payload in the data field. The blank line between events marks the end of an SSE event.

SSE is useful when the server needs to push updates to the client over one long-lived HTTP response. It is simpler than WebSockets when the main requirement is one-way server-to-client updates.

Polling would require the client to make repeated requests to check whether new information is available. WebSockets would be more appropriate if the application needed continuous two-way communication.

In my current implementation, the streaming endpoint fetches weather, places, and currency sequentially, whereas my standard endpoint uses asyncio.gather() for concurrent fetching. A future improvement would be to combine concurrent task execution with progressive event delivery while preserving clear event ordering and error handling.

Goal 4 — Consider how failures from individual external services should affect the overall request
Interviewer: What happens if one external API fails? Should the entire travel plan fail, or should you return the available information?

In my current implementation, the standard endpoint uses asyncio.gather() to fetch the three sections. By default, if one of the awaited operations raises an exception, gather() propagates that exception. My endpoint does not currently implement a complete per-service fallback mechanism, so one provider failure can prevent the complete response from being returned successfully.
For a production travel planning API, I would first distinguish between critical and optional data. For example, if weather information is essential to the user's trip, I might treat its failure differently from the failure of an optional tourist-attractions section.

I would configure timeouts for external requests, handle HTTP and network errors, log the failures, and return clear error information rather than exposing internal exception details.

If partial travel plans are acceptable, I would handle each service result independently and return the available sections along with an explicit status for any failed section. I would not silently represent a failed request as valid empty data.

For the streaming endpoint, I would send a structured error event when a service fails, where possible, and then either continue with the remaining services or terminate the stream according to the defined failure policy.

I would also distinguish an external provider failure from an invalid client request, because they require different HTTP error handling.

The goal is to make the API predictable and resilient even when a dependency is unavailable.

What about retries? “I would use limited retries for transient failures, with a timeout and backoff strategy. I would not retry every error indiscriminately, because invalid requests or authentication failures usually need a different fix. Retries should also be bounded so that they do not increase latency unnecessarily.”
Goal 5 — Propose a responsive architecture for aggregating and streaming travel information
Interviewer: If you had to design this API for a real mobile application with many users, how would you make it responsive, scalable and maintainable?

I would keep the same modular architecture, with FastAPI handling requests, Pydantic models validating the input, and separate services responsible for weather, currency, and places.
First, I would validate the travel request before calling any provider. I would then use asynchronous HTTP clients and concurrently execute independent service operations to reduce unnecessary waiting.

Second, I would maintain a cache with suitable TTL values. For a single application process, an in-memory cache can be sufficient, but for multiple workers or application instances, I would consider Redis so that cached data can be shared.

Third, I would expose two response modes. The standard endpoint would return a complete JSON travel plan, while the streaming endpoint would send status updates and completed sections as they become available.

For the streaming workflow, I would coordinate independent service tasks concurrently and emit results as each task completes, rather than waiting for services one after another. I would also preserve meaningful event names and send explicit error or completion events.

For reliability, I would add provider-specific timeouts, controlled retries, structured error handling and logging. I would also protect API credentials using environment variables or a proper secrets manager.

Finally, I would add tests for date validation, cache expiration, provider failures, concurrent fetching, and SSE event formatting. I would monitor latency, cache-hit rate, external API failures and stream disconnections to identify performance bottlenecks.

This would allow the application to remain modular and responsive as the number of users and external dependencies grows.
