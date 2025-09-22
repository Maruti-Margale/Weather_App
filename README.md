# Weather_App

live demo :https://weatherapp-bymarutimargale.streamlit.app/

## 🔁 Application Flow (Streamlit Version)

The following flowchart shows how the Streamlit weather application works behind the scenes:

```mermaid
graph TD
    A[User opens Streamlit app] --> B[App loads UI components]
    B --> C[User enters city name]
    C --> D[Send request to weather API]
    D --> E[Receive weather data]
    E --> F[Parse temperature, humidity, etc]
    F --> G[Update UI with weather info]
    G --> H[User sees updated data on screen]
```
