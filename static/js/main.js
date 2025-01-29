$(document).ready(function() {
    function loadTrades() {
        $.ajax({
            url: "/api/trades",
            method: "GET",
            success: function(data) {
                let tbody = $("#trades-table tbody");
                tbody.empty();
                data.forEach(trade => {
                    tbody.append(`<tr>
                        <td>${trade.symbol}</td>
                        <td>${trade.quantity}</td>
                        <td>${trade.price}</td>
                        <td>${trade.order_type}</td>
                        <td>${trade.timestamp}</td>
                    </tr>`);
                });
            },
            error: function() {
                alert("Błąd ładowania transakcji!");
            }
        });
    }

    loadTrades();
    setInterval(loadTrades, 10000);  // Odświeżanie co 10s
});
