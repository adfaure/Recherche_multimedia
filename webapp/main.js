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

    initialize : function(data) {
      this.set({
        photo_path : 'index_mult/' + data.exec_path + '/' + data.photo_name
      });
    },

    parse: function (data, opts) {
        if (opts.fetchType == "files") {
          console.log(data)
          console.log(opts)
          return {
            "files" : data
          }
        } else if (opts.fetchType == "results") {
          return {
            "res" : data
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
          $("#results").append(view.render().el);
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
          $("#results").append(view.render().el);
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
          model.set("complete", true);
          model.fetch({ fetchType : "results" })
        }

        if (++intervalCount > 10 | model.get("complete")) {
          clearInterval(checkCallBack)
        }

      }, 2000, model);
    },

    render: function() {
      console.log("render")
      console.log(this.model);
      var template = _.template( $("#results-tmpl").html());
      this.$el.html(template(this.model.toJSON()));

      return this;
    },
  });

});
