var r = new Rune({
  container: "#canvas",
  width: 380,
  height: 380,
  debug: false,
});

$.ajax({
  type: 'GET',
  url: "https://gist.githubusercontent.com/titipata/33bd071df166c135bcd5d87a6b53c32c/raw/e662e0dab90dc37dd615020418770655d4fac522/example_bim.json",
  dataType: 'json',
  success: function(result){
  var x = 0;
  var y = 0;
  var xt = 0;
  var yt = 0;
  for( var i = 0; i < result.length; i++ ) {
    if ( result[i].chat_length.length != 0 ) {
      if( result[i].user_id == 1 ) {
        r.rect(x, y, 2, result[i].char_length)
         .stroke(false)
         .fill(180)

      if( y > r.height ) {
        x += 3;
        y = 0;
        r.rect(x, y, 2, result[i].char_length)
         .stroke(false)
         .fill(180)
        }
      }

      if(result[i].user_id == 0) {
        r.rect(xt, yt, 2, result[i].char_length)
         .stroke(false)
         .fill(0)

        if( yt > r.height) {
          xt += 3;
          yt = 0;
          r.rect(xt, yt, 2, result[i].char_length)
           .stroke(false)
           .fill(0)
        }
      }
      y += result[i].char_length;
      yt += result[i].char_length;
    }
  }
  r.draw();
  }
});
