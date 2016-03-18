$(function(){

  var cfg = JSON.parse($("#data").html());

  var Result = Backbone.Model.extend({

    url: function() {
      if(!this.get("complete")) {
        return cfg.results_url + this.get("exec_path")  + "/";
      } else {
        return cfg.results_url + this.get("exec_path")  + "/" + this.get("photo_name") + '.json';
      }
    },

    toHighCharts : function() {
      if(typeof this.get('res') !== 'undefined') {

        XAxis = [];
        values = [];

        sorted = _.chain(_.map(this.get('res'), function(attr, key) {
          return {
            value : parseFloat(attr.map),
            name : key
          }
        })).sortBy('value').each(function(attr) {
          XAxis.unshift(attr.name);
          values.unshift(attr.value);
        });

        return {
          chart: {
              type: 'bar'
          },
          title : { text : this.get('photo_name') },
          subtitle :  { text : this.get("hello") },
          xAxis : {
            categories : XAxis
          },
          yAxis: {
            min: 0,
            title: {
              text: '%',
              align: 'high'
            },
            labels: {
              overflow: 'justify'
            },
            tooltip: {
              valueSuffix: '%'
            },
          },
          plotOptions: {
            bar: {
              dataLabels: {
                enabled: true
              }
            }
          },
          legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'top',
            x: -40,
            y: 80,
            floating: true,
            borderWidth: 1,
            backgroundColor: ((Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'),
            shadow: true
          },
          credits: {
            enabled: false
          },
          series : [
            {
              name : "map",
              data : values
            }
          ]
        };
      } else return {};
    },
/*

    $('#container').highcharts({
        chart: {
            type: 'bar'
        },
        title: {
            text: 'Historic World Population by Region'
        },
        subtitle: {
            text: 'Source: <a href="https://en.wikipedia.org/wiki/World_population">Wikipedia.org</a>'
        },
        xAxis: {
            categories: ['Africa', 'America', 'Asia', 'Europe', 'Oceania'],
            title: {
                text: null
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Population (millions)',
                align: 'high'
            },
            labels: {
                overflow: 'justify'
            }
        },
        tooltip: {
            valueSuffix: ' millions'
        },
        plotOptions: {
            bar: {
                dataLabels: {
                    enabled: true
                }
            }
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'top',
            x: -40,
            y: 80,
            floating: true,
            borderWidth: 1,
            backgroundColor: ((Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'),
            shadow: true
        },
        credits: {
            enabled: false
        },
        series: [{
            name: 'Year 1800',
            data: [107, 31, 635, 203, 2]
        }, {
            name: 'Year 1900',
            data: [133, 156, 947, 408, 6]
        }, {
            name: 'Year 2012',
            data: [1052, 954, 4250, 740, 38]
        }]
    });
});
*/
    initialize : function(data) {
      this.set({
        photo_path : 'index_mult/' + data.exec_path + '/' + data.photo_name
      });
    },

    parse: function (data, opts) {
      if (opts.fetchType == "files") {
        return {
          "files" : data
        }
      } else if (opts.fetchType == "results") {
        return {
          "res" : data,
          "complete" : true
        };
      } else {
        return data;
      }
    },


    defaults: function() {
      return {
        complete : false,
        error : false
      };
    }
  });

  var AppView = Backbone.View.extend({

    el: $("#evalapp"),

    tagName:  "div",

    events: {
      'click #upload-file-btn ' : 'uploadFile',
      'click #upload-url-btn ' : 'uploadUrl'
    },

    initialize: function() {
      this.listViews = [];
    },

    uploadFile : function() {
      var form_data = new FormData($('#upload-file')[0]);
      var self = this;
      $.ajax({
        type: 'POST',
        url: cfg.eval_url + '/upload',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        async: false,
        success: function(data) {
          var view = new ResultView(new Result(data))
          $("#results").prepend(view.render().el);
          self.listViews.push(view);
        },
      });
    },

    uploadUrl : function() {
      var form_data = new FormData($('#url')[0]);
      var cfg = JSON.parse($("#data").html());
      var self = this;
      $.ajax({
        type: 'POST',
        url: cfg.eval_url +  '/upload_url',
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        async: false,
        success: function(data) {
          var view = new ResultView(new Result(data))
          $("#results").prepend(view.render().el);
          self.listViews.push(view);
        },
      });
    },

    render: function() {
    },
  });

  var App = new AppView;

  var ResultView = Backbone.View.extend({

    tagName : "div",

    cfg : JSON.parse($("#data").html()),

    events: {
    },

    initialize: function(model) {
      this.model = model;
      _.bindAll(this, "render");
      this.model.bind('change:res', this.render);
      var intervalCount = 0;
      var checkCallBack = setInterval(function(intervalModel, clearInt) {
        model.fetch({ fetchType : "files" });
        var completed = _.find(model.get("files"), function(attr) {
          return attr.name == model.get("photo_name") + ".json";
        });

        if(completed) {
          model.set('complete', true);
          model.fetch({ fetchType : "results" })
        }

        if (++intervalCount > 10 | model.get("complete")) {
          clearInterval(checkCallBack)
        }

      }, 2000, model);
    },

    render: function() {
      var template = _.template( $("#results-tmpl").html());
      console.log("hello");
      this.$el.html(template(this.model.toJSON()));
      console.log(this.model)
      if(this.model.get('complete')) {
        this.$(".barchart").highcharts(this.model.toHighCharts());

      }
      return this;
    },
  });

});
