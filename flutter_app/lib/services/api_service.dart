import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user.dart';
import '../models/role.dart';

class ApiService {
  final String baseUrl = 'http://localhost:8000';
  String? _token;

  void setToken(String token) {
    _token = token;
  }

  String? get token => _token;

  Map<String, String> get headers {
    final Map<String, String> headers = {
      'Content-Type': 'application/json',
    };
    if (_token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }
    return headers;
  }

  Future<String> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: {
        'username': email,
        'password': password,
      },
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _token = data['access_token'];
      return _token!;
    } else {
      throw Exception('Falha no login');
    }
  }

  Future<User> getCurrentUser() async {
    final response = await http.get(
      Uri.parse('$baseUrl/auth/me'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      return User.fromJson(json.decode(response.body));
    } else {
      throw Exception('Falha ao buscar usuário atual');
    }
  }

  // User CRUD operations
  Future<List<User>> getUsers() async {
    final response = await http.get(
      Uri.parse('$baseUrl/users/'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((user) => User.fromJson(user)).toList();
    } else {
      throw Exception('Falha ao buscar usuários');
    }
  }

  Future<User> createUser(User user) async {
    final response = await http.post(
      Uri.parse('$baseUrl/users/'),
      headers: headers,
      body: json.encode(user.toJson()),
    );

    if (response.statusCode == 201) {
      return User.fromJson(json.decode(response.body));
    } else {
      throw Exception('Falha ao criar usuário');
    }
  }

  Future<User> updateUser(int id, User user) async {
    final response = await http.put(
      Uri.parse('$baseUrl/users/$id'),
      headers: headers,
      body: json.encode(user.toJson()),
    );

    if (response.statusCode == 200) {
      return User.fromJson(json.decode(response.body));
    } else {
      throw Exception('Falha ao atualizar usuário');
    }
  }

  Future<void> deleteUser(int id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/users/$id'),
      headers: headers,
    );

    if (response.statusCode != 204) {
      throw Exception('Falha ao excluir usuário');
    }
  }

  // Role CRUD operations
  Future<List<Role>> getRoles() async {
    final response = await http.get(
      Uri.parse('$baseUrl/roles/'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((role) => Role.fromJson(role)).toList();
    } else {
      throw Exception('Falha ao buscar roles');
    }
  }

  Future<Role> createRole(Role role) async {
    final response = await http.post(
      Uri.parse('$baseUrl/roles/'),
      headers: headers,
      body: json.encode(role.toJson()),
    );

    if (response.statusCode == 201) {
      return Role.fromJson(json.decode(response.body));
    } else {
      throw Exception('Falha ao criar role');
    }
  }

  Future<Role> updateRole(int id, Role role) async {
    final response = await http.put(
      Uri.parse('$baseUrl/roles/$id'),
      headers: headers,
      body: json.encode(role.toJson()),
    );

    if (response.statusCode == 200) {
      return Role.fromJson(json.decode(response.body));
    } else {
      throw Exception('Falha ao atualizar role');
    }
  }

  Future<void> deleteRole(int id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/roles/$id'),
      headers: headers,
    );

    if (response.statusCode != 204) {
      throw Exception('Falha ao excluir role');
    }
  }
}