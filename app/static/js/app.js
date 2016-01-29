
var app = angular.module('myApp', ['btford.socket-io',
                         'ui.bootstrap',
                         'mgcrea.ngStrap',
                         'akoenig.deckgrid',
                         'angularLazyImg']
)
app.factory('socket', function (socketFactory) {
    var myIoSocket = io.connect('http://' + document.domain + ':' + location.port + "/");

    mySocket = socketFactory({
        ioSocket: myIoSocket
    });
    return mySocket;
});

app.controller('HomeController', function($scope, socket) {
    $scope.comics = [],
    socket.emit('get_comics');

    socket.forward('send_comics', $scope);

    $scope.$on('socket:send_comics', function (ev, data) {
        $scope.comics = data
    });
})

app.controller('SearchController', function($scope, socket){
    $scope.query = "";
    $scope.comics = [],

    socket.emit('get_all_comics');
    socket.forward('send_comics', $scope);

    $scope.$on('socket:send_comics', function (ev, data) {
        $scope.comics = data
    });
})
