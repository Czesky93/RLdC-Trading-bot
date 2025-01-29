function loadTradingView(symbol) {
    new TradingView.widget({
        "container_id": "tradingview_chart",
        "autosize": true,
        "symbol": "BINANCE:" + symbol,
        "interval": "15",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "details": true,
        "studies": ["RSI@tv-basicstudies"]
    });
}

// Pobieranie dostępnych symboli z Binance i dynamiczne tworzenie listy wyboru
function loadSymbols() {
    $.get("https://api.binance.com/api/v3/exchangeInfo", function(data) {
        let select = $("#symbol-select");
        let symbols = data.symbols.map(s => s.symbol).sort();
        select.empty().append('<option value="">Wybierz parę...</option>');
        
        symbols.forEach(symbol => {
            select.append(`<option value="${symbol}">${symbol}</option>`);
        });
        
        // Inicjalizacja pierwszego wykresu po załadowaniu listy
        if (symbols.length > 0) {
            loadTradingView(symbols[0]);
            select.val(symbols[0]);
        }
    });
}

$(document).ready(function() {
    loadSymbols();

    $("#symbol-select").change(function() {
        let newSymbol = $(this).val();
        if (newSymbol) {
            $("#tradingview_chart").html(""); // Czyszczenie starego wykresu
            loadTradingView(newSymbol);
        }
    });
});
