@Repository
public interface AccountRepository extends JpaRepository<Account, UUID> {
    // 특정 유저의 모든 계좌를 찾는 메서드
    List<Account> findByUser_UserId(UUID userId);

    // 계좌 번호로 특정 계좌를 찾는 메서드
    Optional<Account> findByAccountNumber(String accountNumber);
}