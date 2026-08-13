# Building a GraphQL API with Python

## Running the Server

Start the FastAPI application with uvicorn:

```bash
uvicorn main:app --reload
```

The GraphQL endpoint will be available at `http://localhost:8000/graphql/`.

## HTTPie Client

The endpoint expects a JSON body with the GraphQL `query` field, so use `query=@<file>` to embed the raw GraphQL file as a string value.

### Send a query from a file

```bash
http POST http://localhost:8000/graphql/ query=@httpie-requests/hello.graphql
```

This is equivalent to sending the GraphQL query inline:

```bash
http POST http://localhost:8000/graphql/ query='query { hello(name: "Eli") }'
```

### Common pitfalls

- Do **not** send `Content-Type: application/graphql` — the server only accepts `application/json` or `multipart/form-data`.
- Do **not** use `query:=@file.graphql` (with `:=`), because that tells HTTPie to parse the file as JSON. A `.graphql` file is raw text, so use `query=@file.graphql` instead.

### Expected response

```json
{
    "data": {
        "hello": "Hello, Eli"
    }
}
```

## Authentication

Some mutations and queries require an authenticated user. The API expects a bearer token in the `Authorization` header.

### Log in and obtain a token

Use the `loginCandidate` mutation to request a JWT:

```bash
http POST http://localhost:8000/graphql/ query=@httpie-requests/mutations/loginCandidate.graphql
```

Expected response:

```json
{
    "data": {
        "loginCandidate": {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    }
}
```

### Use the bearer token in API calls

Store the token in a shell variable and attach it to subsequent requests:

```bash
TOKEN=$(http POST http://localhost:8000/graphql/ query=@httpie-requests/mutations/loginCandidate.graphql | jq -r '.data.loginCandidate.token')

http POST http://localhost:8000/graphql/ \
    query=@httpie-requests/mutations/addCandidateApplication.graphql \
    Authorization:"Bearer $TOKEN"
```

Or combine the steps into one command:

```bash
http POST http://localhost:8000/graphql/ \
    query=@httpie-requests/mutations/addCandidateApplication.graphql \
    Authorization:"Bearer $(http POST http://localhost:8000/graphql/ query=@httpie-requests/mutations/loginCandidate.graphql | jq -r '.data.loginCandidate.token')"
```

Note the HTTPie header syntax `Header:value`. Because the header value contains a space after `Bearer`, the value must be quoted.

## GraphQL Playground

Once the server is running, open `http://localhost:8000/graphql/` in your browser to use GraphQL Playground.

### Basic usage

1. Write your query in the editor on the left:

    ```graphql
    query {
        employers {
            id
            name
            jobs {
                title
            }
        }
    }
    ```

2. Click the play button (or press `Ctrl+Enter` / `Cmd+Enter`) to execute it.
3. The response appears in the panel on the right.

### Removing autocomplete hints

GraphQL Playground shows inline type hints (e.g. `[EmployerObject]`, `String`) while typing. To remove them, install the browser extension:

- [GQL Hint Remover - Chrome Web Store](https://chromewebstore.google.com/detail/gql-hint-remover/ccemghkcbjdocklnmgppaimcakfbhnjl)

After installing it, reload the Playground tab. The hover/type-hint popups should be suppressed.
