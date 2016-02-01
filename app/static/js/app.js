
var app = angular.module('myApp', ['btford.socket-io',
                         'ui.bootstrap',
                         'mgcrea.ngStrap',
                         'akoenig.deckgrid',
                         'angularLazyImg',
                         'ngAnimate',
                         'ngMaterial']
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
    socket.forward('success', $scope);

    $scope.$on('socket:send_comics', function (ev, data) {
        $scope.comics = data
        for (i = 0; i < $scope.comics.length; i++) {
            $scope.comics[i].hide = false;
        }
    });

    $scope.bought = function(id){
        socket.emit('bought', id)
        for (i = 0; i < $scope.comics.length; i++) {
            if ($scope.comics[i].id === id) {
                $scope.comics[i].hide = true;
            }
        }
    }
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

    $scope.$watch('hideme', function() {
       $scope.$emit('lazyImg:refresh');
    });

    $scope.select = function(key,data) {
        $scope.key = key;
        $scope.selected = data;
        $scope.hideme = ! $scope.hideme;
    }
    $scope.selected = {};

    $scope.unbought = function(id){
        socket.emit('unbought', id)
    }
})

app.controller('SearchController', function($scope, socket){
    $scope.query = ""
    $scope.hideme = false
    $scope.comics = []

    $scope.$watch('query', function() {
       $scope.$emit('lazyImg:refresh');
    });

    socket.emit('get_all_comics');
    socket.forward('send_comics', $scope);

    $scope.$on('socket:send_comics', function (ev, data) {
        $scope.comics = data
    });

    $scope.$watch('hideme', function() {
       $scope.$emit('lazyImg:refresh');
    });

    $scope.select = function(key,data) {
        $scope.key = key;
        $scope.selected = data;
        $scope.hideme = ! $scope.hideme;
    }
    $scope.selected = {};

    $scope.unbought = function(id){
        socket.emit('unbought', id)
    }
})
