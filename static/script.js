$(document).ready(function() {
    $('input[type="file"]').on('change', function() {
        var formData = new FormData();
        formData.append('file', this.files[0]);

        $.ajax({
            url: '/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(shortNames) {
                var shortNamesContainer = $('#shortNamesContainer');
                shortNamesContainer.empty();

                shortNames.forEach(function(shortName) {
                    var checkbox = $('<input>')
                        .attr('type', 'checkbox')
                        .attr('name', 'short_names[]')
                        .attr('value', shortName)
                        .addClass('short-name-checkbox');
                    var label = $('<label>').text(shortName);

                    var container = $('<div>').addClass('short-name-item');
                    container.append(checkbox).append(label);
                    shortNamesContainer.append(container);
                });
            }
        });
    });

    $('#searchBar').on('input', function() {
        var filter = $(this).val().toLowerCase();
        var filteredItems = $('.short-name-item').filter(function() {
            return $(this).find('input').val().toLowerCase().includes(filter);
        });

        $('#shortNamesContainer').html(filteredItems);
    });

    $('#transformButton').on('click', function() {
        var formData = new FormData($('#uploadForm')[0]);

        $.ajax({
            url: '/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.status === 'success') {
                    var downloadLink = $('<a>')
                        .attr('href', response.file_url)
                        .text('Download Transformed File');
                    $('#downloadContainer').html(downloadLink);
                }
            }
        });
    });
});
