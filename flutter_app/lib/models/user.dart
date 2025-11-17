class User {
  final int? id;
  final String email;
  final String name;
  final String? profileImageUrl;
  final String? profileImageBase64;
  final int? roleId;
  final String? roleName;

  User({
    this.id,
    required this.email,
    required this.name,
    this.profileImageUrl,
    this.profileImageBase64,
    this.roleId,
    this.roleName,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      name: json['name'],
      profileImageUrl: json['profile_image_url'],
      profileImageBase64: json['profile_image_base64'],
      roleId: json['role_id'],
      roleName: json['role_name'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'profile_image_url': profileImageUrl,
      'profile_image_base64': profileImageBase64,
      'role_id': roleId,
    };
  }
}