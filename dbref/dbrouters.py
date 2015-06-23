		
class DBRefRouter(object):
  def db_for_read(self, model, ** hints):
    if model._meta.app_label == 'dbref':
      return 'dbref'
    return None
			
  def db_for_write(self, model, ** hints):
    if model._meta.app_label == 'dbref':
      return 'dbref'
    return None
			
  def allow_relation(self, obj1, obj2, ** hints):
    if obj1._meta.app_label == 'dbref' and obj2._meta.app_label == 'dbref':
      return True
    return None
			
  def allow_migrate(self, db, model):
    if db == 'dbref':
      return model._meta.app_label == 'dbref'
    elif model._meta.app_label == 'dbref':
      return False
    return None
