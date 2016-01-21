<script type="text/javascript" charset="utf-8">
  $(document).ready(function(){
      namespace = ''; // change to an empty string to use the global namespace


      $('a.buy').on('click', function(){
        var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
        var $comic_id = this.getAttribute('desc')

        $(this).text('Added to collection')
        $(this).toggleClass("disabled");
        socket.emit('buy', {data: $comic_id});
        socket.emit('disconnect request');
        return false;
      });
      $('a[href="' + this.location.pathname + '"]').parents('li,ul').addClass('active');
      $('.pop').on('click', function() {
            var image_ids = $(this).find('img').map(function(){return $(this).attr("comic-id");}).get();
            var $list = $('#imagesList');
            $.each(image_ids, function(i, src) {
              var $div = $("<div>", {class:"col-lg-6 col-md-6 col-sm-6 col-xs-12"});
              var $hover = $("<div>", {class:"hovereffect"});
              var $img = $("<img>", {id:this, class:"img-responsive", src:"https://s3-us-west-1.amazonaws.com/comicbooktime/covers/"+ this+ ".jpg"});
              var $overlay = $('<div>', {class:"overlay"});
              $overlay.append("<h2></h2><p><a class='unbuy info' desc=" + this + "><i class='fa fa-times fa-5x'></i></a>");
              $div.append($hover.append($img).append($overlay));

              $('#imagesList').append($div);
            });
            $('#imagemodal').modal('show');   

      $('a.unbuy.info').on('click', function () {
        var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
        var $comic_id = this.getAttribute('desc')
        $('img#' + $comic_id).remove()
        socket.emit('unbuy', {data: $comic_id});
        socket.emit('disconnect request');

        return false;
      });
      });		

      $('#imagemodal').on('hidden.bs.modal', function () {
          $(this).find("#imagesList").empty();

      });
});
      
</script>
