$('.toggle-comment').each(function () {
  $(this).click(function () {
      var content = $(this).text();
      if(content != '收起神回复'){
          $(this).html("<i class='z-icon-comment'></i>收起神回复");
          $(this).parent().parent().parent().next().css('display', 'block');
          $(this).parent().addClass('focusIn');
      }
      else {
          var num = parseInt($(this).attr('num'));
          $(this).html("<i class='z-icon-comment'></i>神回复");
          $(this).parent().parent().parent().next().css('display', 'none');
          $(this).parent().removeClass('focusIn');
      }
  })
})
