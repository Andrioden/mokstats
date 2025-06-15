$(document).ready(function() {
	// Add a button that - by using ajax - loads the last games player list.
	var loadPlayersButton = $('<input type="button" class="left" value="Use last playerlist (no save)">');
	loadPlayersButton.on("click", loadLastMatchPlayers);
	$('.submit-row').append(loadPlayersButton);
});

function loadLastMatchPlayers() {
    var playersTable = $('#playerresult_set-group').find('table').first();

    $.get('/ajax/last_playerlist/', function(data) {
        $(data).each(function(i, id) {
            var playerRowCount = playersTable.find('select').length - 1;
            if (i > playerRowCount-1)
                $('.add-row').find('a')[0].click(); //New player row
            playersTable.find('select').eq(i).val(id);
        });
    },'json');
}
