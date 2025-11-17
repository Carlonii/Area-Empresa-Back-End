import 'package:flutter/material.dart';
import '../models/role.dart';
import '../services/api_service.dart';

class RolesScreen extends StatefulWidget {
  final ApiService apiService;

  const RolesScreen({Key? key, required this.apiService}) : super(key: key);

  @override
  _RolesScreenState createState() => _RolesScreenState();
}

class _RolesScreenState extends State<RolesScreen> {
  List<Role> roles = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadRoles();
  }

  Future<void> _loadRoles() async {
    try {
      setState(() => isLoading = true);
      final loadedRoles = await widget.apiService.getRoles();
      setState(() {
        roles = loadedRoles;
        isLoading = false;
      });
    } catch (e) {
      setState(() => isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao carregar roles: $e')),
      );
    }
  }

  Future<void> _showRoleDialog({Role? role}) async {
    final nameController = TextEditingController(text: role?.name ?? '');
    final descriptionController = TextEditingController(text: role?.description ?? '');

    return showDialog<void>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(role == null ? 'Nova Role' : 'Editar Role'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: InputDecoration(labelText: 'Nome'),
              ),
              SizedBox(height: 16),
              TextField(
                controller: descriptionController,
                decoration: InputDecoration(labelText: 'Descrição'),
                maxLines: 3,
              ),
            ],
          ),
          actions: <Widget>[
            TextButton(
              child: Text('Cancelar'),
              onPressed: () => Navigator.of(context).pop(),
            ),
            ElevatedButton(
              child: Text(role == null ? 'Criar' : 'Salvar'),
              onPressed: () async {
                if (nameController.text.trim().isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Nome é obrigatório')),
                  );
                  return;
                }

                try {
                  final roleData = Role(
                    id: role?.id,
                    name: nameController.text.trim(),
                    description: descriptionController.text.trim().isEmpty 
                        ? null 
                        : descriptionController.text.trim(),
                  );

                  if (role == null) {
                    await widget.apiService.createRole(roleData);
                  } else {
                    await widget.apiService.updateRole(role.id!, roleData);
                  }

                  Navigator.of(context).pop();
                  _loadRoles();
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(role == null 
                        ? 'Role criada com sucesso' 
                        : 'Role atualizada com sucesso')),
                  );
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Erro ao salvar role: $e')),
                  );
                }
              },
            ),
          ],
        );
      },
    );
  }

  Future<void> _deleteRole(Role role) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Confirmar Exclusão'),
          content: Text('Tem certeza que deseja excluir a role "${role.name}"?'),
          actions: <Widget>[
            TextButton(
              child: Text('Cancelar'),
              onPressed: () => Navigator.of(context).pop(false),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              child: Text('Excluir'),
              onPressed: () => Navigator.of(context).pop(true),
            ),
          ],
        );
      },
    );

    if (confirmed == true) {
      try {
        await widget.apiService.deleteRole(role.id!);
        _loadRoles();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Role "${role.name}" excluída com sucesso')),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro ao excluir role: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Gerenciamento de Roles'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _loadRoles,
          ),
        ],
      ),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : roles.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.security, size: 64, color: Colors.grey),
                      SizedBox(height: 16),
                      Text('Nenhuma role encontrada'),
                      SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () => _showRoleDialog(),
                        child: Text('Criar primeira role'),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  itemCount: roles.length,
                  itemBuilder: (context, index) {
                    final role = roles[index];
                    return Card(
                      margin: EdgeInsets.all(8),
                      child: ListTile(
                        leading: CircleAvatar(
                          child: Icon(Icons.security),
                        ),
                        title: Text(role.name),
                        subtitle: role.description != null 
                            ? Text(role.description!)
                            : Text('Sem descrição'),
                        trailing: PopupMenuButton<String>(
                          onSelected: (value) {
                            if (value == 'edit') {
                              _showRoleDialog(role: role);
                            } else if (value == 'delete') {
                              _deleteRole(role);
                            }
                          },
                          itemBuilder: (BuildContext context) => [
                            PopupMenuItem(
                              value: 'edit',
                              child: Row(
                                children: [
                                  Icon(Icons.edit),
                                  SizedBox(width: 8),
                                  Text('Editar'),
                                ],
                              ),
                            ),
                            PopupMenuItem(
                              value: 'delete',
                              child: Row(
                                children: [
                                  Icon(Icons.delete, color: Colors.red),
                                  SizedBox(width: 8),
                                  Text('Excluir', style: TextStyle(color: Colors.red)),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showRoleDialog(),
        child: Icon(Icons.add),
        tooltip: 'Nova Role',
      ),
    );
  }
}