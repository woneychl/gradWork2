@Service
public class UserService {
    @Autowired
    private UserRepository userRepository; // 레포지토리 주입

    public User getUserByEmail(String email) {
        // findByEmail을 호출하면 스프링이 자동으로 SELECT 쿼리를 날려 유저를 찾습니다.
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("유저를 찾을 수 없습니다."));
    }
}