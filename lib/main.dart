import 'package:flutter/material.dart';

void main() => runApp(const DialogerApp());

class DialogerApp extends StatelessWidget {
  const DialogerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Dialoger',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Изучаем немецкий")),
      body: Center(
        child: Column(
          children: [
            ElevatedButton(
              onPressed: () => Navigator.push(context, MaterialPageRoute(
                  builder: (context) => const CardsScreen())),
              child: const Text("Карточки"),
            ),
            // Другие кнопки...
          ],
        ),
      ),
    );
  }
}