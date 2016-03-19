$(function(){

  var cfg = JSON.parse($("#data").html());

  var Message = Backbone.Model.extend({

    initialize : function(message) {
      this.set({
        "message"  : message
      });
    },

    defaults: function() {
      return {
        "message" : ""
      };
    }
  });

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

    initialize : function(data) {
      //console.log(data);
      if(!data.exec_path) {
        this.set({
          valid : true,
          exec_path : data.name,
          photo_path : "",
          photo_name : "",
          concepts : []
        });
      } else {
        this.set({
          photo_path : 'index_mult/' + data.exec_path + '/' + data.photo_name,
          concepts : [],
          valid : true
        });
      }
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
      } else if (opts.fetchType == "raw") {

        photo_name = _.find(data, function(elem) {
          ext = elem.name.split('.').pop();
          return _.contains(['JPG','jpg','png','PNG'], ext);
        });

        res_file = _.find(data, function(elem) {
          ext = elem.name.split('.').pop();
          return _.contains(['json'], ext);
        });

        if(!photo_name) {
          return  {
            valid : false
          }
        }

        complete = true;
        if(!res_file) {
          valid : true,
          complete = false;
        }

        return {
          valid : true,
          complete : false,
          files : data,
          photo_name : photo_name.name,
          photo_path : 'index_mult/' + this.get('exec_path') + '/' + photo_name.name
        }
      } else {
        return data;
      }
    },


    defaults: function() {
      return {
        complete : false,
        error : false,
        valid : true
      };
    }
  });

  var Results = Backbone.Collection.extend({
    model: Result,
    url: 'http://eval/index_mult/',

    initialize : function(a,b,c) {
      this.on('add', this.addOne);
      this.urls = [];
    },

    parse : function(data, opts) {
      return data;
    },

    paginate : function(page, size) {
      return this.models.slice(page * 2 ,(page * 2) + size);
    },

    addOne : function(model, collection) {
      var self = this;
      model.fetch({ fetchType : "raw",
      success : function(model) {
        if(!model.get('valid')) {
          self.remove(model);
          return;
        }
        if(model.get("complete")) {
          model.fetch({fetchType : "results"});
        }
      }
    });

  }
});


var AppView = Backbone.View.extend({

  el: $("#evalapp"),

  tagName:  "div",

  events: {

    'click #upload-file-btn ' : 'uploadFile',
    'click #upload-url-btn ' : 'uploadUrl'
  },

  paginate : function() {
    var self = this;
    _.each(this.collection.paginate(this.currentPage, 2), function(model) {
      if(model.get("valid")) {
        self.currentPage++;
        var view = new ResultView(model);
        $("#results").prepend(view.render().el);
        self.listViews.push(view);
      } else {
        console.log("not valid")
      }
    });
  },

  initialize: function() {
    var self = this;
    this.currentPage = 0;
    this.listViews = [];
    this.collection = new Results();
    this.collection.fetch({
      data: { page: this.currentPage},
      remove: false
    });
    
    $(window).scroll(function() {
       if($(window).scrollTop() + $(window).height() == $(document).height()) {
           self.paginate();
       }
    });

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
      error: function(err) {
        var view = new AlertView(new Message(err.responseText))
        $("#alerts").prepend(view.render().el);
      }
    });
  },

  uploadUrl : function() {
    var cfg = JSON.parse($("#data").html());
    var url =  $('#input-url').val();
    var self = this;
    $.ajax({
      type: 'POST',
      url: cfg.eval_url +  '/upload_url',
      data: JSON.stringify({ url : url }),
      contentType: false,
      cache: false,
      processData: false,
      async: false,
      success: function(data) {
        var view = new ResultView(new Result(data))
        $("#results").prepend(view.render().el);
        self.listViews.push(view);
      },
      error : function(err) {
        var view = new AlertView(new Message(err.responseText))
        $("#alerts").prepend(view.render().el);
      }
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
    this.model.bind('change:concepts', this.render);

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

      if (++intervalCount > 1000 | model.get("complete")) {
        clearInterval(checkCallBack)
      }

    }, 2000, model);
  },

  render: function() {
    var template = _.template( $("#results-tmpl").html());
    this.$el.html(template(this.model.toJSON()));
    if(this.model.get('complete')) {
      var concepts = _.filter(this.model.get('res'), function(elem) {
        return elem.is_concept === "1";
      });
      this.model.set("concepts", concepts);
      this.$(".barchart").highcharts(this.model.toHighCharts());
    }
    return this;
  },
});


var AlertView = Backbone.View.extend({

  tagName : "div",

  events: {
  },

  destroy_view: function() {

    // COMPLETELY UNBIND THE VIEW
    this.undelegateEvents();

    this.$el.removeData().unbind();

    // Remove view from DOM
    this.remove();
    Backbone.View.prototype.remove.call(this);

  },

  initialize: function(model) {
    this.model = model;
    setTimeout(this.destroy_view.bind(this), 10000);
  },

  render: function() {
    var template = _.template( $("#alert-tmpl").html());
    this.$el.html(template(this.model.toJSON()));
    return this;
  },
});

});
