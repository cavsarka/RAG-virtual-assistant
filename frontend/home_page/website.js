async function submitQuery() {
    event.preventDefault();

    const query = document.getElementById('query').value;

    // Show a loading message or spinner if desired
    const responseBox = document.getElementById('response')
    const sourceBox = document.getElementById('source')
    responseBox.innerText = "Loading...";

    const response = await fetch('http://127.0.0.1:5000/query_openai', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
    });
    const result = await response.json();
    console.log(result)
    responseBox.innerText = result.response;
    sourceBox.innerText = "Source: " + result.source;
}
