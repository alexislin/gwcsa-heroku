function updateShare(shareType) {
    var shareQuantity = parseInt($("#" + shareType + "_quantity").val());
    var shareSize = $("#" + shareType + "_size option:selected").val();
    var sharePrice = parseInt($("#" + shareType + "_price").text());


    if (shareSize == "half") {
        sharePrice = parseInt($("#" + shareType + "_halfprice").text());
    }

    $("#" + shareType + "_total").text(shareQuantity * sharePrice);

    updateTotal();
}

function updateTotal() {
    var total = 0;

    $(".share_total").each(function() {
        total += parseInt($(this).text());
    });

    $("#total").text(total);
}

$(function() {
    $(".share_size").change(function() {
        var shareType = $(this).attr("name").split("_")[0];
        updateShare(shareType);
    });

    $(".share_quantity").change(function() {
        var shareType = $(this).attr("name").split("_")[0];
        updateShare(shareType);
    });

    // initialize the page totals
    $(".share_size").each(function() {
        var shareType = $(this).attr("name").split("_")[0];
        updateShare(shareType);
    });

    $(".tip").tipsy({html: true});
});
