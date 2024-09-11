$(document).ready(function() {
    
    $('table.table').DataTable({
      sDom: "<'row'<'col-sm-12'f>><'row'<'col-sm-12'tr>><'row'<'col-sm-4'l><'col-sm-4'p><'col-sm-4 text-right'i>>",
      oLanguage: {
        sEmptyTable: "Nenhum registro encontrado",
        sInfo: "Exibindo: _START_ - _END_ de _TOTAL_ registros",
        sInfoEmpty: "0 itens",
        sInfoFiltered: "(Filtrar de _MAX_ total registros)",
        sInfoPostFix: "",
        sInfoThousands: ".",
        sLengthMenu: "Registros por página: _MENU_",
        sLoadingRecords: "",
        sProcessing: "",
        sZeroRecords: "Nenhum registro encontrado",
        sSearch: "Pesquisar",
        oPaginate: {
          sNext: "Próximo",
          sPrevious: "Anterior",
          sFirst: "Primeiro",
          sLast: "Último"
        },
        oAria: {
          sSortAscending: ": Ordem ascendente",
          sSortDescending: ": Ordem descendente"
        }
      }
    });

    // Valor - Caixa Alta
    $('.valMaiusculo').bind('keyup', function (e) {

      if (e.which >= 97 && e.which <= 122) {
          var newKey = e.which - 32;
          e.keyCode = newKey;
          e.charCode = newKey;
      }

      var oldVal = $(this).val();
      var newVal = oldVal.toUpperCase();

      if (oldVal != newVal) {
          $(this).val(newVal);
      }

  });

  // Valor - Caixa Baixa
  $('.valMinusculo').bind('keyup', function (e) {

      if (e.which >= 97 && e.which <= 122) {
          var newKey = e.which - 32;
          e.keyCode = newKey;
          e.charCode = newKey;
      }

      var oldVal = $(this).val();
      var newVal = oldVal.toLowerCase();

      if (oldVal != newVal) {
          $(this).val(newVal);
      }

  });

  $('.maskMoeda').mask('000.000.000.000.000.00', {reverse: true})
    .attr('placeholder', '0.00')
    .attr('type', 'number')
    .attr('min', '0.00')
    .attr('max', '9999999999.99')
    .attr('step', '0.01')
    .css('text-align', 'right');

  $('.maskNumero')
    .attr('placeholder', '0')
    .attr('type', 'number')
    .attr('min', '0')
    .attr('max', '9999999999')
    .attr('step', '1')
    .css('text-align', 'right');

  $('.maskPeriodo').mask('00/0000')
    .attr('placeholder', 'MM/AAAA')
    .css('text-align', 'right');

});