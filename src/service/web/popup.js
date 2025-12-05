document.getElementById("send").onclick = async () => {
    const product = document.getElementById("product").value;
    const price = parseFloat(document.getElementById("price").value);

    const res = await fetch("http://localhost:8000/api/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product, price })
    });

    alert("Ответ сервера: " + (await res.text()));
};
