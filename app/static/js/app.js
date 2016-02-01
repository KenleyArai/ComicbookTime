
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

app.controller('MyCollection', function($scope, socket) {
    $scope.series = [],
    $scope.hideme = false,
    $scope.key = "",
    socket.emit('get_collection');

    socket.forward('send_comics', $scope);

    $scope.$on('socket:send_comics', function (ev, data) {
        $scope.series = data
    });

    $scope.select = function(key,data) {
        $scope.key = key;
        $scope.selected = data;
        $scope.hideme = ! $scope.hideme;
    }
    $scope.selected = {};
})

app.controller('SearchController', function($scope, socket){
    $scope.query = "";
    $scope.comics = [],

    $scope.$watch('query', function() {
       $scope.$emit('lazyImg:refresh');
    });

    socket.emit('get_all_comics');
    socket.forward('send_comics', $scope);

    $scope.$on('socket:send_comics', function (ev, data) {
        $scope.comics = data
    });
})
