document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    const data = {};
    formData.forEach((value, key) => { data[key] = value; });
    fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(response => response.json()).then(data => alert(JSON.stringify(data)));
});

document.getElementById('transactionForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    const data = {};
    formData.forEach((value, key) => { data[key] = value; });
    fetch('/transaction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(response => response.json()).then(data => alert(JSON.stringify(data)));
});

function getTransactions() {
    const userId = document.getElementById('userId').value;
    fetch(`/transactions/${userId}`, {
        method: 'GET'
    }).then(response => response.json()).then(data => {
        const transactionsDiv = document.getElementById('transactions');
        transactionsDiv.innerHTML = '';
        data.forEach(transaction => {
            transactionsDiv.innerHTML += `<p>${JSON.stringify(transaction)}</p>`;
        });
    });
}
