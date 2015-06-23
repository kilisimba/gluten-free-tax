		
class DBRefRouter(object):
  def db_for_read(self, model, ** hints):
    if model._meta.app_label == 'achat':
      return 'achat'
    return None
			
  def db_for_write(self, model, ** hints):
    if model._meta.app_label == 'achat':
      return 'achat'
    return None
			
  def allow_relation(self, obj1, obj2, ** hints):
    if obj1._meta.app_label == 'achat' and obj2._meta.app_label == 'achat':
      return True
    return None
			
  def allow_migrate(self, db, model):
    if db == 'achat':
      return model._meta.app_label == 'achat'
    elif model._meta.app_label == 'achat':
      return False
    return None
