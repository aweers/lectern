# Advanced Features Demo

This post showcases more advanced capabilities of the blog system.

## Working with Images

You can embed images easily:

![Sample Image](/assets/img/profile.webp)

*Caption: This is where your image caption would go*

## Tables

Create formatted tables:

| Feature | Supported | Notes |
| :--- | :--- | :--- |
| Markdown | Yes | Full GFM support |
| LaTeX Math | Yes | Inline and display |
| Code Highlighting | Yes | Many languages |
| Citations | Yes | BibTeX format |

## Advanced Math

For more complex equations, you can use aligned environments:

$$
\begin{align*}
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\
\nabla \times \mathbf{B} &= \mu_0 \mathbf{J} + \mu_0 \epsilon_0 \frac{\partial \mathbf{E}}{\partial t} \\
\nabla \cdot \mathbf{E} &= \frac{\rho}{\epsilon_0} \\
\nabla \cdot \mathbf{B} &= 0
\end{align*}
$$

## Multi-Language Code Support

### JavaScript Example

```javascript
const fibonacci = (n) => {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
};

console.log(fibonacci(10));
```

### Rust Example

```rust
fn factorial(n: u64) -> u64 {
    match n {
        0 | 1 => 1,
        _ => n * factorial(n - 1),
    }
}

fn main() {
    println!("Factorial of 5: {}", factorial(5));
}
```

## Blockquotes

> "The best way to predict the future is to invent it."
> 
> — Alan Kay

## Nested Lists

You can create complex nested structures:

1. First main point
   - Sub-point A
   - Sub-point B
     - Nested item 1
     - Nested item 2
2. Second main point
   - Another sub-point
   - Yet another one

## Horizontal Rules

Use horizontal rules to separate sections:

---

## Conclusion

These advanced features allow you to create rich, technical content with ease. Experiment with different combinations to find what works best for your content!
